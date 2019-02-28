var done = 0;
(function wait () {if (!done) setTimeout(wait, 1000);})();

const jsonld = require('jsonld');

const line = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#nil> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>.\n<file://bn614X>  <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>."
jsonld.fromRDF(line, {format: 'application/n-quads'}, (err, doc) => {
            if (err) {
              console.log("err" + err)
            } else {
              console.log("doc"+doc)
            }
            done = true
});
