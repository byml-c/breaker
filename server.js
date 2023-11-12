const express = require('express');
const login = require('./login');

const app = express();
var bodyParser = require('body-parser');
app.use(bodyParser());

app.post('/login', function (req, res) {
    let result = req.body;
    let tmp = '';

    function _etd(_p0) {
        try {
            var _p2 = login.encryptAES(_p0, result.seed);
            tmp = _p2;
        } catch (e) {
            tmp = _p0;
        }
    }
    function _etd2(_p0, _p1) {
        console.log(_p0, _p1);
        try {
            var _p2 = login.encryptAES(_p0, _p1);
            tmp = _p2;
        } catch (e) {
            tmp = _p0;
        }
    }
    _etd2(result.password, result.seed);
    console.log(tmp);
    res.send(tmp);
});

app.listen(1117, () => {
    console.log('Router on port 1177 has been opened successfully!');
});