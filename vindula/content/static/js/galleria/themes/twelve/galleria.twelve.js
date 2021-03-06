/*
 Galleria Twelve Theme 2011-02-18
 http://galleria.aino.se

 Copyright (c) 2011, Aino
*/
(function (r) {
    Galleria.addTheme({
        name: "twelve",
        author: "Galleria",
        css: "galleria.twelve.css",
        defaults: {
            transition: "pulse",
            transitionSpeed: 500,
            imageCrop: true,
            thumbCrop: true,
            carousel: false,
            _locale: {
                show_thumbnails: "Show thumbnails",
                hide_thumbnails: "Hide thumbnails",
                play: "Play slideshow",
                pause: "Pause slideshow",
                enter_fullscreen: "Enter fullscreen",
                exit_fullscreen: "Exit fullscreen",
                popout_image: "Popout image",
                showing_image: "Showing image %s of %s"
            },
            _showFullscreen: true,
            _showPopout: true,
            _showProgress: true,
            _showTooltip: true
        },
        init: function (c) {
            this.addElement("bar", "fullscreen", "play", "popout", "thumblink", "s1", "s2", "s3", "s4", "progress");
            this.append({
                stage: "progress",
                container: ["bar", "tooltip"],
                bar: ["fullscreen", "play", "popout", "thumblink", "info", "s1", "s2", "s3", "s4"]
            });
            this.prependChild("info", "counter");
            var a = this,
                o = this.$("thumbnails-container"),
                h = this.$("thumblink"),
                f = this.$("fullscreen"),
                j = this.$("play"),
                k = this.$("popout"),
                i = this.$("bar"),
                l = this.$("progress"),
                s = c.transition,
                d = c._locale,
                e = false,
                m = false,
                g = !! c.autoplay,
                p = false,
                q = function () {
                    o.height(a.getStageHeight())
                        .width(a.getStageWidth())
                        .css("top", e ? 0 : a.getStageHeight() + 30)
                };
            q();
            c._showTooltip && a.bindTooltip({
                thumblink: d.show_thumbnails,
                fullscreen: d.enter_fullscreen,
                play: d.play,
                popout: d.popout_image,
                caption: function () {
                    var b = a.getData(),
                        n = "";
                    if (b) {
                        if (b.title && b.title.length) n += "<strong>" + b.title + "</strong>";
                        if (b.description && b.description.length) n += "<br>" + b.description
                    }
                    return n
                },
                counter: function () {
                    return d.showing_image.replace(/\%s/, a.getIndex() + 1)
                        .replace(/\%s/, a.getDataLength())
                }
            });
            this.bind("play", function () {
                g = true;
                j.addClass("playing")
            });
            this.bind("pause", function () {
                g = false;
                j.removeClass("playing");
                l.width(0)
            });
            c._showProgress && this.bind("progress", function (b) {
                l.width(b.percent / 100 * this.getStageWidth())
            });
            this.bind("loadstart", function (b) {
                b.cached || this.$("loader")
                    .show()
            });
            this.bind("loadfinish", function () {
                l.width(0);
                this.$("loader")
                    .hide();
                this.refreshTooltip("counter", "caption")
            });
            this.bind("thumbnail", function (b) {
                r(b.thumbTarget)
                    .hover(function () {
                    a.setInfo(b.thumbOrder);
                    a.setCounter(b.thumbOrder)
                }, function () {
                    a.setInfo();
                    a.setCounter()
                })
                    .click(function () {
                    h.click()
                })
            });
            this.bind("fullscreen_enter", function () {
                m = true;
                a.setOptions("transition", "none");
                f.addClass("open");
                i.css("bottom", 0);
                this.defineTooltip("fullscreen", d.exit_fullscreen);
                this.addIdleState(i, {
                    bottom: -31
                })
            });
            this.bind("fullscreen_exit", function () {
                m = false;
                Galleria.utils.clearTimer("bar");
                a.setOptions("transition", s);
                f.removeClass("open");
                i.css("bottom", 0);
                this.defineTooltip("fullscreen", d.enter_fullscreen);
                this.removeIdleState(i, {
                    bottom: -31
                })
            });
            this.bind("rescale", q);
            this.addIdleState(this.get("image-nav-left"), {
                left: -36
            });
            this.addIdleState(this.get("image-nav-right"), {
                right: -36
            });
            h.click(function () {
                if (e && p) a.play();
                else {
                    p = g;
                    a.pause()
                }
                o.animate({
                    top: e ? a.getStageHeight() + 30 : 0
                }, {
                    easing: "galleria",
                    duration: 400,
                    complete: function () {
                        a.defineTooltip("thumblink", e ? d.show_thumbnails : d.hide_thumbnails);
                        h[e ? "removeClass" : "addClass"]("open");
                        e = !e
                    }
                })
            });
            if (c._showPopout) k.click(function (b) {
                a.openLightbox();
                b.preventDefault()
            });
            else {
                k.remove();
                if (c._showFullscreen) {
                    this.$("s4")
                        .remove();
                    this.$("info")
                        .css("right", 40);
                    f.css("right", 0)
                }
            }
            j.click(function () {
                a.defineTooltip("play", g ? d.play : d.pause);
                if (g) a.pause();
                else {
                    e && h.click();
                    a.play()
                }
            });
            if (c._showFullscreen) f.click(function () {
                m ? a.exitFullscreen() : a.enterFullscreen()
            });
            else {
                f.remove();
                if (c._show_popout) {
                    this.$("s4")
                        .remove();
                    this.$("info")
                        .css("right", 40);
                    k.css("right", 0)
                }
            }
            if (!c._showFullscreen && !c._showPopout) {
                this.$("s3,s4")
                    .remove();
                this.$("info")
                    .css("right", 10)
            }
        }
    })
})(jQuery);