class PdfCanvas {
    constructor(c) {
        this.canvas = c;
        this.pdf = null;
        this.pageNumber = 1;
        this.rotation = 0;
    }

    load = (url) => {
        const {pdfjsLib} = globalThis;
        pdfjsLib.GlobalWorkerOptions.workerSrc
            = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';
        const loadingTask = pdfjsLib.getDocument(url);
        loadingTask.promise.then((pdf) => {
            this.pdf = pdf;
        });
    }

    feed = (pageNumber) => {
        pageNumber = this.pdf._pdfInfo.numPages < pageNumber ? this.pdf._pdfInfo.numPages : pageNumber;
        this.pdf.getPage(pageNumber).then(this.render);
    }

    render = (page) => {
        const viewport = page.getViewport({scale: 1, rotation: this.rotation});
        const ctx = this.canvas.getContext('2d', {willReadFrequently: true});
        this.canvas.height = viewport.height;
        this.canvas.width = viewport.width;
        const renderCtx = {canvasContext: ctx, viewport: viewport};
        page.render(renderCtx);
    }

    prev = () => {
        this.pageNumber = this.pageNumber === 1 ? 1 : this.pageNumber - 1;
        this.feed(this.pageNumber);
    }

    next = () => {
        this.pageNumber = this.pdf._pdfInfo.numPages === this.pageNumber ? this.pageNumber : this.pageNumber + 1;
        this.feed(this.pageNumber);
    }

    rotateLeft90 = () => {
        this.rotation = this.rotation === 0 ? 270 : this.rotation - 90;
        this.feed(this.pageNumber);
    }

    rotateRight90 = () => {
        this.rotation = this.rotation === 270 ? 0 : this.rotation + 90;
        this.feed(this.pageNumber);
    }
}

window.onload = () => {
    document.getElementById('next').addEventListener('click', next);
    document.getElementById('prev').addEventListener('click', prev);
    document.getElementById('left90').addEventListener('click', rotateLeft90);
    document.getElementById('right90').addEventListener('click', rotateRight90);
}

let pdfCanvas = null;

function next() {
    pdfCanvas.next();
}

function prev() {
    pdfCanvas.prev();
}

function rotateLeft90() {
    pdfCanvas.rotateLeft90();
}

function rotateRight90() {
    pdfCanvas.rotateRight90();
}

export function load(url) {
    pdfCanvas = new PdfCanvas(document.getElementById('pdf-canvas'));
    pdfCanvas.load(url);
}
