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
