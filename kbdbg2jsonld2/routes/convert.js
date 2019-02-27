var express = require('express');
var router = express.Router();

const N3 = require('n3');

router.post('/', function(req, res, next) {
  //console.log(req.body['n3'])
  const parser = new N3.Parser(format='N3');
  const writer = N3.Writer({ prefixes: { c: 'http://example.org/cartoons#' } });
  parser.parse(req.body['n3'], (error, quad, prefixes) => {
    if (error) {
      console.log(error)
    }
    if (quad)
    {
      console.log("quad:"+quad)
      writer.addQuad(quad)
    }
    else
      writer.end((error, result) => {
        console.log("err?:"+error)
        console.log(result)
        res.send(result)
      });
  })
});

module.exports = router;
