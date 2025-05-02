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
    request.open('GET', this.thumb_url + "?id=" + e.getAttribute('id') + "&content=encoded");
    request.responseType = 'text';
    request.onload = () => e.src = request.responseText;
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

const SlideShow = function (w, i) {
    if (!(this instanceof SlideShow)) {
        return new SlideShow(w, i);
    }

    this.window = w;
    this.interval = undefined;
    this.interval_ms = i;
}

SlideShow.prototype.start = function () {
    const targets = Array.from(this.window.document.querySelectorAll('[data-lightbox]')).map(image => image.getAttribute('href'));
    if (targets.length === 0) {
        return;
    }
    let index = 0;
    this.interval = setInterval(() => {
        this.load(targets[index]);
        index = (index + 1) % targets.length;
    }, this.interval_ms);
}

SlideShow.prototype.load = (target) => fetch(target)
    .then(res => res.arrayBuffer())
    .then(bytes => {
        const url = URL.createObjectURL(new Blob([new Uint8Array(bytes)], {type: 'image/png'}));
        const i = this.window.document.getElementById('slide-show-image');
        i.onload = () => URL.revokeObjectURL(url);
        i.src = url;
    });

SlideShow.prototype.stop = function () {
    clearInterval(this.interval);
}