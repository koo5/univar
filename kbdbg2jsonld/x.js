const N3 = require('n3');
var fs = require('fs');





/*
fs. readFile('DATA', 'utf8', function(err, n3_text) {
//console.log(n3_text);

const parser = new N3.Parser();
wait.for (parser.parse(n3_text, (error, quad, prefixes) => {
    if (quad)
      console.log(quad);
    else
      console.log("# That's all, folks!", prefixes);
  }));

//const writer = N3.Writer({ prefixes: { c: 'http://example.org/cartoons#' } });
jsonld.fromRDF(nquads, {format: 'application/n-quads'}, (err, doc) => {
  // doc is JSON-LD
  console.log(err,doc)
});
});*/







async function businessLogic() {
	const result = await function ()  {
		return new Promise((resolve, reject) => {
			fs. readFile('DATA', 'utf8', function(err, n3_text) {
			const parser = new N3.Parser();
			parser.parse(n3_text, (error, quad, prefixes) => {
				if (quad)
					console.log(quad);
				else
					console.log("# That's all, folks!", prefixes);
					resolve(1);
				});

			});
		})
	}
	console.log(result);
}

// call the main function
await businessLogic();
