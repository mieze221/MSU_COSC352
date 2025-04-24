FROM elixir:latest


WORKDIR /app


COPY project2.exs .


CMD ["elixir", "project2.exs"]
    