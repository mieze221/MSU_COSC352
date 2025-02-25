
;; (ns hello-name-c
;;   (:gen-class))

;; (defn -main
;;   [& args]
;;   (if (= (count args) 2)
;;     (let [name (first args)
;;           count (Integer/parseInt (second args))]
;;       (dotimes [_ count]
;;         (println (str "Hello, " name "!"))))
;;     (println "Usage: hello-name-c <name> <count>" args)))

;; (-main)

(def args *command-line-args*)  ;; Get arguments
 (println "Arguments received:" args)

 (if (= (count args) 2)
   (let [name (first args)
         count (Integer. (second args))]
     (dotimes [_ count]
       (println (str "Hello, " name "!"))))
   (println "Usage: hello-name-c <name> <count>"))
