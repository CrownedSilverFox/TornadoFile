let progress;
let done_blocks = [];
let blocks;

async function get_part(start, end, url) {
    let headers = new Headers();
    headers.append("Range", "bytes=" + start + "-" + end);
    let request = new Request(url, {headers: headers});
    let response = (await fetch(request)).blob().then(function (myBlob) {
        return myBlob;
    });
    response = await response;
    done_blocks.push(start);
    progress = 100*(done_blocks.length/blocks);
    $('.progress-bar').attr('aria-valuenow', Number(Math.ceil(progress))).text(Number(Math.ceil(progress)) + '%').css('width', Number(Math.ceil(progress))+'%');
    return response;
}

function get_content(chunks) {
    let file = $('#FileSelect option:selected');
    file = file.text();
    let size;
    file = file.split(': ');
    size = Number(file[1]);
    file = file[0];
    let url = "http://localhost:8888/get/" + file;
    let chunk_size = Math.floor(size / chunks);
    let bytes = [];
    for (let i = 0; i < size; i += chunk_size) {
        bytes.push(i);
    }
    if ((bytes[bytes.length - 1]) !== size) {
        bytes[bytes.length - 1] = size+1;
    }
    blocks = bytes.length;
    done_blocks = [];
    progress = 0;
    let promises = [];
    for (let i = 1; i < bytes.length; i++) {
        promises.push(get_part(bytes[i - 1], bytes[i]-1, url));
    }
    let blob;
    Promise.all(promises).then(function (results) {
        blob = new Blob(results);
        $('.progress-bar').attr('aria-valuenow', 100).text(100 + '%').css('width', 100 + '%');
        download(blob, file);
    });
}
