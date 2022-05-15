const DelayedImageLoader = function (w, url) {
    if (!(this instanceof DelayedImageLoader)) {
        return new DelayedImageLoader(w, url);
    }

    this.window = w;
    this.thumb_url = url;
}

DelayedImageLoader.prototype.scroll = function () {
    let y = this.window.scrollY;
    let h = this.window.innerHeight;
    let images = this.window.document.getElementsByClassName('lazy');
    for (let i = 0; i < images.length; i++) {
        let pos = images[i].getBoundingClientRect().top + y;
        if (y > pos - h) {
            this.focus(images[i]);
        }
    }
}

DelayedImageLoader.prototype.focus = function (e) {
    if (!e.hasAttribute('id')) {
        return;
    }

    let request = new XMLHttpRequest();
    request.open('GET', this.thumb_url + "?id=" + e.getAttribute('id') + "&thumb=yes");
    request.responseType = 'text';
    request.onload = function () {
        e.src = request.responseText;
    }
    request.send();
    e.removeAttribute('id');
}

const TileSwitch = function (w, id, type, page) {
    if (!(this instanceof TileSwitch)) {
        return new TileSwitch(w, id, type, page);
    }

    this.window = w;
    this.id = id;
    this.type = type;
    this.page = page;
}

TileSwitch.prototype.changed = function (ev) {
    if (ev.currentTarget.checked) {
        this.window.location.href = '?id=' + this.id + '&type=' + this.type + '&page=' + this.page + '&tile=true';
    } else {
        this.window.location.href = '?id=' + this.id + '&type=' + this.type + '&page=' + this.page;
    }
}

const PdfCanvas = function (w, url) {
    if (!(this instanceof PdfCanvas)) {
        return new PdfCanvas(w, url);
    }

    this.window = w;
    this.url = url;
    this.pdf = null;
}

PdfCanvas.prototype.load = function () {
    const pdfjsLib = this.window['pdfjs-dist/build/pdf'];
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';
    const loadingTask = pdfjsLib.getDocument(this.url);
    loadingTask.promise.then(this.loaded);
}

PdfCanvas.prototype.loaded = function (pdf) {
    pdfCanvas.pdf = pdf;
    pdfCanvas.feed(1);
}

PdfCanvas.prototype.feed = function (pageNumber) {
    pageNumber = this.pdf._pdfInfo.numPages < pageNumber ? this.pdf._pdfInfo.numPages : pageNumber;
    this.pdf.getPage(pageNumber).then(this.render);
}

PdfCanvas.prototype.render = function (page) {
    const viewport = page.getViewport({scale: 1});
    const canvas = this.window.document.getElementById('pdf-canvas');
    const ctx = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    const renderCtx = {
        canvasContext: ctx,
        viewport: viewport,
    };
    page.render(renderCtx);
}
