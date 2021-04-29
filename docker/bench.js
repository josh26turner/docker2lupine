const express = require('express');
const app = express();

app.get('/', (_, res) => {
    const n = 40000000;
    const a = new Array(n);
    for (let i = 0; i < n; i++) a[i] = i*i;
    for (let i = 0; i < n; i++) a[i] = Math.sqrt(i);
    res.send();
})

app.listen(3000, () => {})