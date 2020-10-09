$(function () {
    var options = {
        cellHeight: '10vh',
        verticalMargin: '2vh',
        width: 3,
        disableDrag: true,
        disableResize: true
    };
    $('.grid-stack').gridstack(options);
});

let url = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '');
let socket = io.connect(url + '/update');
socket.on('tileUpdate', function (msg) {
    let data = JSON.parse(msg);
    let node = document.querySelector('#tile-' + data["uniqueName"] + ' .container');

    if (node === null) {
        return;
    }

    if (data["content"] === null) {
        node.innerHTML = '<div class="placeholder">❌ Data not yet available</div>';
        return;
    }

    node.innerHTML = data["content"];

    // scripts have to be added dynamically instead of "innerHTML"
    // (otherwise they won't be executed due to browser code injection counter measurements)
    let scriptTags = node.querySelectorAll('script');
    for (script of scriptTags) {
        var newScript = document.createElement("script");
        var inlineScript = document.createTextNode(script.innerText);
        newScript.appendChild(inlineScript);
        script.parentNode.appendChild(newScript);
        script.remove();
    }
});

$('.grid-stack-item').click(function () {
    let tileName = this.id.replace('tile-', '');
    console.log('Manual refresh for tile "' + tileName + '"');
    socket.emit('refresh', tileName);
});