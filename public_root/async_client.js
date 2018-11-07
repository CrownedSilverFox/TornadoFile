async function get_part(start, end, url) {
    let headers = new Headers();
    headers.append("Range", "bytes=" + start + "-" + end);
    let request = new Request(url, {headers: headers});
    let mBlob = new Blob();
    let response = (await fetch(request)).blob().then(function (myBlob) {
        return myBlob;
    });
    return response;
}

function get_content(chunks) {
    let file = document.getElementById('FileSelect');
    file = file.options[file.selectedIndex].text;
    let size;
    file = file.split(': ');
    size = Number(file[1]);
    file = file[0];
    console.log(file);
    console.log(size);
    let url = "http://localhost:8888/get/" + file;
    let chunk_size = Math.floor(size / chunks);
    let bytes = [];
    for (let i = 0; i < size; i += chunk_size) {
        bytes.push(i);
    }
    if ((bytes[bytes.length - 1]) !== size) {
        bytes[bytes.length - 1] = size+1;
    }
    let promises = [];
    for (let i = 1; i < bytes.length; i++) {
        promises.push(get_part(bytes[i - 1], bytes[i]-1, url));
    }
    let blob;
    Promise.all(promises).then(function (results) {
        console.log(results);
        blob = new Blob(results);
        download(blob, file);
        // console.log(blob.size)
    });
}