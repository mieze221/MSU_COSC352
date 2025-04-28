const std = @import("std");

const c = @cImport({
    @include("libxml/parser.h");
    @include("libxml/tree.h");
    @include("libxml/HTMLparser.h");
});

const fs = std.fs;
const allocator = std.heap.page_allocator;

fn cStrEq(cstr: [*:0]const u8, str: []const u8) bool {
    return std.mem.eql(u8, std.mem.span(cstr), str);
}

fn node_to_text(node: *c.xmlNode) []const u8 {
    const content = c.xmlNodeGetContent(node);
    if (content == null) return "";
    defer c.xmlFree(content);

    const c_str = std.mem.span(std.mem.cast([*:0]u8, content));
    const buf = allocator.alloc(u8, c_str.len) catch return "";
    std.mem.copy(u8, buf, c_str);
    return buf;
}

fn extract_tables(file: []const u8, file_id: usize) !void {
    const f = try fs.cwd().openFile(file, .{ .read = true });
    defer f.close();

    const content = try f.readToEndAlloc(allocator, 10 * 1024);
    defer allocator.free(content);

    const doc = c.htmlReadMemory(content.ptr, @intCast(c_int, content.len), null, null, c.HTML_PARSE_NOERROR | c.HTML_PARSE_NOWARNING);
    if (doc == null) return error.ParseFailed;
    defer c.xmlFreeDoc(doc);

    var node = c.xmlDocGetRootElement(doc);
    var table_idx: usize = 0;

    while (node != null) : (node = node.*.next) {
        if (node.*.type == c.XML_ELEMENT_NODE and cStrEq(node.*.name, "table")) {
            table_idx += 1;
            var csv = std.ArrayList(u8).init(allocator);
            defer csv.deinit();

            var row = node.*.children;
            while (row != null) : (row = row.*.next) {
                if (row.*.type == c.XML_ELEMENT_NODE and cStrEq(row.*.name, "tr")) {
                    var cell = row.*.children;
                    while (cell != null) : (cell = cell.*.next) {
                        if (cell.*.type == c.XML_ELEMENT_NODE and (cStrEq(cell.*.name, "td") or cStrEq(cell.*.name, "th"))) {
                            const text = node_to_text(cell);
                            try csv.appendSlice(text);
                            try csv.append(',');
                        }
                    }
                    try csv.appendSlice("\n");
                }
            }

            const out_name = try std.fmt.allocPrint(allocator, "output_{d}_table_{d}.csv", .{file_id, table_idx});
            defer allocator.free(out_name);

            const out = try fs.cwd().createFile(out_name, .{ .read = false });
            defer out.close();
            try out.writeAll(csv.items);
        }
    }
}

fn process_file(path: []const u8, id: usize) void {
    const res = extract_tables(path, id);
    if (res) |err| {
        std.debug.print("Failed to process {s}: {}\n", .{path, err});
    }
}

fn run_sequential(paths: [][]const u8) void {
    const timer = std.time.Timer.start() catch {
        std.debug.print("Failed to start timer\n", .{});
        return;
    };
    for (paths) |path, idx| {
        process_file(path, idx);
    }
    const elapsed = timer.read();
    std.debug.print("Sequential Execution Time: {d:.2} seconds\n", .{@as(f64, @floatFromInt(elapsed)) / 1_000_000_000});
}

fn run_multithreaded(paths: [][]const u8) void {
    const timer = std.time.Timer.start() catch {
        std.debug.print("Failed to start timer\n", .{});
        return;
    };

    var threads = std.ArrayList(std.Thread).init(allocator);
    defer threads.deinit();

    for (paths) |path, idx| {
        const thread = std.Thread.spawn(.{}, process_file, .{ path, idx }) catch {
            std.debug.print("Failed to spawn thread for {s}\n", .{path});
            continue;
        };
        threads.append(thread) catch {};
    }

    for (threads.items) |*t| t.join();

    const elapsed = timer.read();
    std.debug.print("Multithreaded Execution Time: {d:.2} seconds\n", .{@as(f64, @floatFromInt(elapsed)) / 1_000_000_000});
}

pub fn main() void {
    const file_paths = [_][]const u8{
        "data/page1.html",
        "data/page2.html",
        "data/page3.html",
    };

    std.debug.print("--- Sequential Mode ---\n", .{});
    run_sequential(&file_paths);

    std.debug.print("--- Multithreaded Mode ---\n", .{});
    run_multithreaded(&file_paths);
}
