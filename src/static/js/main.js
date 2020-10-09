let options = {
    cellHeight: '10vh',
    margin: '2vh',
    column: 12,
    disableDrag: true,
    disableResize: true,
};

let grid = GridStack.init(options);


let url = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '');
let socket = io.connect(url + '/update');
socket.on('tileUpdate', function(msg)
{
    let data = JSON.parse(msg);
    let node = document.querySelector('#tile-' + data["uniqueName"] + ' .container');

    if(node === null)
    {
        return;
    }

    if(data["content"] === null)
    {
        node.innerHTML = '<div class="placeholder">❌ Data not yet available</div>';
        return;
    }

    node.innerHTML = data["content"];

    // scripts have to be added dynamically instead of "innerHTML"
    // (otherwise they won't be executed due to browser code injection counter measurements)
    let scriptTags = node.querySelectorAll('script');
    for(script of scriptTags)
    {
        let newScript = document.createElement("script");
        let inlineScript = document.createTextNode(script.innerText);
        newScript.appendChild(inlineScript);
        script.parentNode.appendChild(newScript);
        script.remove();
    }
});

let items = document.querySelectorAll('.grid-stack-item');
for(let i = 0; i < items.length; i++)
{
    items[i].addEventListener('click', function(event)
    {
        let tileName = this.id.replace('tile-', '');
        console.log('Manual refresh for tile "' + tileName + '"');
        socket.emit('refresh', tileName);
    });
}
