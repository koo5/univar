var express = require('express');
var router = express.Router();

const N3 = require('n3');
const jsonld = require('jsonld');

router.post('/', function(req, res, next) {
  //console.log(req.body['n3'])
  const parser = new N3.Parser(format='N3');
  const writer = N3.Writer({ format: 'N-Triples' });
  parser.parse(req.body['n3'], (error, quad, prefixes) => {
    if (error) {
      console.log(error)
    }
    if (quad)
    {
      //console.log("quad:"+quad)
      writer.addQuad(quad)
    }
    else {
      console.log("end..")
      writer.end((error, result) => {
        if (error) {
          console.log("err?:" + error)
          res.send(error)
        } else {
          //console.log("result?"+result)
          jsonld.fromRDF(result, {}, (err, doc) => {
            if (err) {
              console.log("doc" + doc)
              console.log("err" + err)
              res.status(500).send({ error: err });
            } else {
              for (o in doc){
                //console.log("aaa:"+o)
                //console.log(doc[o])
              }

              var frame = req.body['frame']
              //console.log("frame:"+frame)
              jsonld.frame(doc, frame, (err, framed) => {
                if (err) {
                  console.log("errr " + err)
                  res.status(500).send({ error: err });
                } else {
                  res.send(framed)
                }
              });
              //console.log(doc)
              //res.send(doc)
            }
          });
        }
      });
    }
  })
});

module.exports = router;
