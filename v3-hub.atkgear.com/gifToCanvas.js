"use strict";
var __assign =
  (this && this.__assign) ||
  function () {
    __assign =
      Object.assign ||
      function (t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
          s = arguments[i];
          for (var p in s)
            if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
        }
        return t;
      };
    return __assign.apply(this, arguments);
  };
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }

    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }

      function rejected(value) {
        try {
          step(generator["throw"](value));
        } catch (e) {
          reject(e);
        }
      }

      function step(result) {
        result.done
          ? resolve(result.value)
          : adopt(result.value).then(fulfilled, rejected);
      }

      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
var __generator =
  (this && this.__generator) ||
  function (thisArg, body) {
    var _ = {
        label: 0,
        sent: function () {
          if (t[0] & 1) throw t[1];
          return t[1];
        },
        trys: [],
        ops: [],
      },
      f,
      y,
      t,
      g;
    return (
      (g = { next: verb(0), throw: verb(1), return: verb(2) }),
      typeof Symbol === "function" &&
        (g[Symbol.iterator] = function () {
          return this;
        }),
      g
    );

    function verb(n) {
      return function (v) {
        return step([n, v]);
      };
    }

    function step(op) {
      if (f) throw new TypeError("Generator is already executing.");
      while (_)
        try {
          if (
            ((f = 1),
            y &&
              (t =
                op[0] & 2
                  ? y["return"]
                  : op[0]
                  ? y["throw"] || ((t = y["return"]) && t.call(y), 0)
                  : y.next) &&
              !(t = t.call(y, op[1])).done)
          )
            return t;
          if (((y = 0), t)) op = [op[0] & 2, t.value];
          switch (op[0]) {
            case 0:
            case 1:
              t = op;
              break;
            case 4:
              _.label++;
              return { value: op[1], done: false };
            case 5:
              _.label++;
              y = op[1];
              op = [0];
              continue;
            case 7:
              op = _.ops.pop();
              _.trys.pop();
              continue;
            default:
              if (
                !((t = _.trys), (t = t.length > 0 && t[t.length - 1])) &&
                (op[0] === 6 || op[0] === 2)
              ) {
                _ = 0;
                continue;
              }
              if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) {
                _.label = op[1];
                break;
              }
              if (op[0] === 6 && _.label < t[1]) {
                _.label = t[1];
                t = op;
                break;
              }
              if (t && _.label < t[2]) {
                _.label = t[2];
                _.ops.push(op);
                break;
              }
              if (t[2]) _.ops.pop();
              _.trys.pop();
              continue;
          }
          op = body.call(thisArg, _);
        } catch (e) {
          op = [6, e];
          y = 0;
        } finally {
          f = t = 0;
        }
      if (op[0] & 5) throw op[1];
      return { value: op[0] ? op[1] : void 0, done: true };
    }
  };
var __spreadArrays =
  (this && this.__spreadArrays) ||
  function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++)
      s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
      for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
        r[k] = a[j];
    return r;
  };
// exports.__esModule = true;
// exports.GifToCanvas = void 0;
// Generic functions
var bitsToNum = function (ba) {
  return ba.reduce(function (s, n) {
    return s * 2 + Number(n);
  }, 0);
};
var byteToBitArr = function (bite) {
  var a = [];
  for (var i = 7; i >= 0; i--) {
    a.push(!!(bite & (1 << i)));
  }
  return a;
};
/**
 * Reading Data
 *
 * @class Stream
 */
var Stream = /** @class */ (function () {
  function Stream(data) {
    this.pos = 0;
    this.data = data;
  }

  Stream.prototype.readByte = function () {
    if (this.pos >= this.data.length) {
      throw new Error("Attempted to read past end of stream.");
    }
    if (this.data instanceof Uint8Array) return this.data[this.pos++];
    else return this.data.charCodeAt(this.pos++) & 0xff;
  };
  Stream.prototype.readBytes = function (n) {
    var bytes = [];
    for (var i = 0; i < n; i++) {
      bytes.push(this.readByte());
    }
    return bytes;
  };
  Stream.prototype.read = function (n) {
    var s = "";
    for (var i = 0; i < n; i++) {
      s += String.fromCharCode(this.readByte());
    }
    return s;
  };
  Stream.prototype.readUnsigned = function () {
    var a = this.readBytes(2);
    return (a[1] << 8) + a[0];
  };
  return Stream;
})();
/**
 * Conversion request returnedGifdata
 *
 * @class ParseGif
 */
var ParseGif = /** @class */ (function () {
  function ParseGif(stream, handler) {
    this.stream = stream;
    this.handler = handler;
  }

  ParseGif.prototype.init = function () {
    var _this = this;
    return new Promise(function (resolve, reject) {
      _this.parseHeader();
      var timer = setTimeout(function () {
        clearTimeout(timer);
        try {
          _this.parseBlock();
          resolve(null);
        } catch (e) {
          reject(e);
        }
      }, 0);
    });
  };
  ParseGif.prototype.parseBlock = function () {
    var block = {};
    block.sentinel = this.stream.readByte();
    switch (
      String.fromCharCode(block.sentinel) // For ease of matching
    ) {
      case "!":
        block.type = "ext";
        this.parseExt(block);
        break;
      case ",":
        block.type = "img";
        this.parseImg(block);
        break;
      case ";":
        block.type = "eof";
        this.handler.eof(block);
        break;
      default:
        throw new Error("Unknown block: 0x" + block.sentinel.toString(16)); // TODO: Pad this with a 0.
    }
    if (block.type !== "eof") {
      this.parseBlock();
    }
  };
  ParseGif.prototype.parseCT = function (entries) {
    // Each entry is 3 bytes, for RGB.
    var ct = [];
    for (var i = 0; i < entries; i++) {
      ct.push(this.stream.readBytes(3));
    }
    return ct;
  };
  ParseGif.prototype.lzwDecode = function (minCodeSize, data) {
    // TODO: Now that the GIF parser is a bit different, maybe this should get an array of bytes instead of a String?
    var pos = 0; // Maybe this streaming thing should be merged with the Stream?
    var readCode = function (size) {
      var code = 0;
      for (var i = 0; i < size; i++) {
        if (data.charCodeAt(pos >> 3) & (1 << (pos & 7))) {
          code |= 1 << i;
        }
        pos++;
      }
      return code;
    };
    var output = [];
    var clearCode = 1 << minCodeSize;
    var eoiCode = clearCode + 1;
    var codeSize = minCodeSize + 1;
    var dict = [];
    var clear = function () {
      dict = [];
      codeSize = minCodeSize + 1;
      for (var i = 0; i < clearCode; i++) {
        dict[i] = [i];
      }
      dict[clearCode] = [];
      dict[eoiCode] = null;
    };
    var code;
    var last;
    while (true) {
      last = code;
      code = readCode(codeSize);
      if (code === clearCode) {
        clear();
        continue;
      }
      if (code === eoiCode) break;
      if (code < dict.length) {
        if (last !== clearCode) {
          dict.push(dict[last].concat(dict[code][0]));
        }
      } else {
        if (code !== dict.length) throw new Error("Invalid LZW code.");
        dict.push(dict[last].concat(dict[last][0]));
      }
      // eslint-disable-next-line prefer-spread
      output.push.apply(output, dict[code]);
      if (dict.length === 1 << codeSize && codeSize < 12) {
        // If we're at the last code and codeSize is 12, the next code will be a clearCode, and it'll be 12 bits long.
        codeSize++;
      }
    }
    // I don't know if this is technically an error, but some GIFs do it.
    //if (Math.ceil(pos / 8) !== data.length) throw new Error('Extraneous LZW bytes.');
    return output;
  };
  ParseGif.prototype.parseImg = function (img) {
    var st = this.stream;
    var deinterlace = function (pixels, width) {
      // Of course this defeats the purpose of interlacing. And it's *probably*
      // the least efficient way it's ever been implemented. But nevertheless...
      var newPixels = new Array(pixels.length);
      var rows = pixels.length / width;
      var cpRow = function (toRow, fromRow) {
        var fromPixels = pixels.slice(fromRow * width, (fromRow + 1) * width);
        // eslint-disable-next-line prefer-spread
        newPixels.splice.apply(
          newPixels,
          __spreadArrays([toRow * width, width], fromPixels)
        );
      };
      // See appendix E.
      var offsets = [0, 4, 2, 1];
      var steps = [8, 8, 4, 2];
      var fromRow = 0;
      for (var pass = 0; pass < 4; pass++) {
        for (var toRow = offsets[pass]; toRow < rows; toRow += steps[pass]) {
          cpRow(toRow, fromRow);
          fromRow++;
        }
      }
      return newPixels;
    };
    img.leftPos = st.readUnsigned();
    img.topPos = st.readUnsigned();
    img.width = st.readUnsigned();
    img.height = st.readUnsigned();
    var bits = byteToBitArr(st.readByte());
    img.lctFlag = bits.shift();
    img.interlaced = bits.shift();
    img.sorted = bits.shift();
    img.reserved = bits.splice(0, 2);
    img.lctSize = bitsToNum(bits.splice(0, 3));
    if (img.lctFlag) {
      img.lct = this.parseCT(1 << (img.lctSize + 1));
    }
    img.lzwMinCodeSize = st.readByte();
    var lzwData = this.readSubBlocks();
    img.pixels = this.lzwDecode(img.lzwMinCodeSize, lzwData);
    if (img.interlaced) {
      // Move
      img.pixels = deinterlace(img.pixels, img.width);
    }
    this.handler.img(img);
  };
  ParseGif.prototype.readSubBlocks = function () {
    var size, data;
    data = "";
    do {
      size = this.stream.readByte();
      data += this.stream.read(size);
    } while (size !== 0);
    return data;
  };
  ParseGif.prototype.parseExt = function (block) {
    var _this = this;
    var parseGCExt = function (block) {
      _this.stream.readByte(); // Always 4
      var bits = byteToBitArr(_this.stream.readByte());
      block.reserved = bits.splice(0, 3); // Reserved; should be 000.
      block.disposalMethod = bitsToNum(bits.splice(0, 3));
      block.userInput = bits.shift();
      block.transparencyGiven = bits.shift();
      block.delayTime = _this.stream.readUnsigned();
      block.transparencyIndex = _this.stream.readByte();
      block.terminator = _this.stream.readByte();
      _this.handler.gce(block);
    };
    var parseComExt = function (block) {
      var _a, _b;
      block.comment = _this.readSubBlocks();
      (_b = (_a = _this.handler).com) === null || _b === void 0
        ? void 0
        : _b.call(_a, block);
    };
    var parsePTExt = function (block) {
      var _a, _b;
      // No one *ever* uses this. If you use it, deal with parsing it yourself.
      _this.stream.readByte(); // Always 12
      block.ptHeader = _this.stream.readBytes(12);
      block.ptData = _this.readSubBlocks();
      (_b = (_a = _this.handler).pte) === null || _b === void 0
        ? void 0
        : _b.call(_a, block);
    };
    var parseAppExt = function (block) {
      var parseNetscapeExt = function (block) {
        _this.stream.readByte(); // Always 3
        block.unknown = _this.stream.readByte(); // ??? Always 1? What is this?
        block.iterations = _this.stream.readUnsigned();
        block.terminator = _this.stream.readByte();
        _this.handler.app.NETSCAPE(block);
      };
      var parseUnknownAppExt = function (block) {
        var _a, _b;
        block.appData = _this.readSubBlocks();
        // FIXME: This won't work if a handler wants to match on any identifier.
        (_b = (_a = _this.handler.app)[block.identifier]) === null ||
        _b === void 0
          ? void 0
          : _b.call(_a, block);
      };
      _this.stream.readByte(); // Always 11
      block.identifier = _this.stream.read(8);
      block.authCode = _this.stream.read(3);
      switch (block.identifier) {
        case "NETSCAPE":
          parseNetscapeExt(block);
          break;
        default:
          parseUnknownAppExt(block);
          break;
      }
    };
    var parseUnknownExt = function (block) {
      var _a, _b;
      block.data = _this.readSubBlocks();
      (_b = (_a = _this.handler).unknown) === null || _b === void 0
        ? void 0
        : _b.call(_a, block);
    };
    block.label = this.stream.readByte();
    switch (block.label) {
      case 0xf9:
        block.extType = "gce";
        parseGCExt(block);
        break;
      case 0xfe:
        block.extType = "com";
        parseComExt(block);
        break;
      case 0x01:
        block.extType = "pte";
        parsePTExt(block);
        break;
      case 0xff:
        block.extType = "app";
        parseAppExt(block);
        break;
      default:
        block.extType = "unknown";
        parseUnknownExt(block);
        break;
    }
  };
  ParseGif.prototype.parseHeader = function () {
    var stream = this.stream;
    var hdr = {};
    hdr.sig = stream.read(3);
    hdr.ver = stream.read(3);
    if (hdr.sig !== "GIF") throw new Error("Not a GIF file."); // XXX: This should probably be handled more nicely.
    hdr.width = stream.readUnsigned();
    hdr.height = stream.readUnsigned();
    var bits = byteToBitArr(stream.readByte());
    hdr.gctFlag = bits.shift();
    hdr.colorRes = bitsToNum(bits.splice(0, 3));
    hdr.sorted = bits.shift();
    hdr.gctSize = bitsToNum(bits.splice(0, 3));
    hdr.bgColor = stream.readByte();
    hdr.pixelAspectRatio = stream.readByte(); // if not 0, aspectRatio = (pixelAspectRatio + 15) / 64
    if (hdr.gctFlag) {
      hdr.gct = this.parseCT(1 << (hdr.gctSize + 1));
    }
    this.handler.hdr(hdr);
  };
  return ParseGif;
})();
var Player = /** @class */ (function () {
  function Player(options) {
    this.playing = false;
    this.forward = true;
    this.i = -1;
    this.options = {
      loopDelay: 0,
      autoPlay: false,
    };
    this.options = __assign(__assign({}, this.options), options);
  }

  Player.prototype.putFrame = function () {
    var _a;
    this.i = parseInt(String(this.i), 10);
    if (this.i > this.options.frames.length - 1) {
      this.i = 0;
    }
    if (this.i < 0) {
      this.i = 0;
    }
    var targetOffset = this.options.targetOffset;
    var offset = this.options.frameOffsets[this.i];
    (_a = this.options.tmpCanvas.getContext("2d")) === null || _a === void 0
      ? void 0
      : _a.putImageData(this.options.frames[this.i].data, offset.x, offset.y);
    var ctx = this.options.canvas.getContext("2d");
    ctx.globalCompositeOperation = "copy";
    ctx.drawImage(
      this.options.tmpCanvas,
      targetOffset.dx,
      targetOffset.dy,
      targetOffset.sWidth,
      targetOffset.sHeight,
      0,
      0,
      targetOffset.sWidth,
      targetOffset.sHeight
    );
  };
  Player.prototype.getNextFrameNo = function () {
    var delta = this.forward ? 1 : -1;
    return (
      (this.i + delta + this.options.frames.length) % this.options.frames.length
    );
  };
  Player.prototype.stepFrame = function (amount) {
    this.i = this.i + amount;
    this.putFrame();
  };
  Player.prototype.step = function () {
    var _this = this;
    var stepping = false;
    var timer = null;
    var completeLoop = function () {
      var _a, _b;
      if (_this.options.autoPlay) {
        doStep();
      } else {
        stepping = false;
        _this.playing = false;
        (_b = (_a = _this.options).onClear) === null || _b === void 0
          ? void 0
          : _b.call(_a);
      }
    };
    var doStep = function () {
      var _a, _b, _c, _d, _e, _f;
      timer && clearTimeout(timer);
      stepping = _this.playing;
      if (!stepping) return;
      _this.stepFrame(1);
      var delay =
        ((_a = _this.options.frames[_this.i].delay) !== null && _a !== void 0
          ? _a
          : 0) * 10;
      if (!delay) delay = 100; // FIXME: Should this even default at all? What should it be?
      var nextFrameNo = _this.getNextFrameNo();
      if (nextFrameNo === 0) {
        (_c = (_b = _this.options).onFrameFinish) === null || _c === void 0
          ? void 0
          : _c.call(_b, _this.options.canvas, delay);
        delay +=
          (_d = _this.options.loopDelay) !== null && _d !== void 0 ? _d : 0;
        timer = setTimeout(completeLoop, delay);
      } else {
        (_f = (_e = _this.options).onFrame) === null || _f === void 0
          ? void 0
          : _f.call(_e, _this.options.canvas, delay);
        timer = setTimeout(doStep, delay);
      }
    };
    doStep();
  };
  Player.prototype.play = function () {
    this.playing = true;
    this.step();
  };
  Player.prototype.init = function () {
    this.play();
  };
  return Player;
})();
/**
 * Git转Canvas
 *
 * @export
 * @class GifToCanvas
 */
var GifToCanvas = /** @class */ (function () {
  function GifToCanvas(url, options) {
    if (options === void 0) {
      options = {};
    }
    this.listener = {};
    this.options = {
      hasCanvasDom: false,
      autoPlay: false,
      targetOffset: {
        dx: 0,
        dy: 0,
      },
    };
    this.hdr = {};
    this.handler = {};
    this.tmpCanvas = document.createElement("canvas");
    this.transparency = null;
    this.disposalMethod = null;
    this.lastDisposalMethod = null;
    this.disposalRestoreFromIdx = null;
    this.delay = null;
    this.lastImg = null;
    this.frame = null;
    this.frames = [];
    this.frameOffsets = [];
    this.options = __assign(__assign({}, this.options), options);
    this.url = url;
    this.canvas = GifToCanvas.canvas =
      this.options.canvasEl ||
      GifToCanvas.canvas ||
      document.createElement("canvas");
  }

  GifToCanvas.prototype.init = function () {
    return __awaiter(this, void 0, void 0, function () {
      return __generator(this, function (_a) {
        switch (_a.label) {
          case 0:
            if (this.options.hasCanvasDom) {
              this.initDom();
            }
            return [4 /*yield*/, this.load()];
          case 1:
            _a.sent();
            return [2 /*return*/];
        }
      });
    });
  };
  GifToCanvas.prototype.initDom = function () {
    if (!this.options.canvasEl) {
      document.body.appendChild(this.canvas);
    }
  };
  GifToCanvas.prototype.load = function () {
    return __awaiter(this, void 0, void 0, function () {
      var data, stream, parseGIF, player;
      return __generator(this, function (_a) {
        switch (_a.label) {
          case 0:
            return [4 /*yield*/, this.createXhr(this.url)];
          case 1:
            data = _a.sent();
            stream = new Stream(data);
            this.handler = this.createHandle();
            parseGIF = new ParseGif(stream, this.handler);
            return [4 /*yield*/, parseGIF.init()];
          case 2:
            _a.sent();
            player = new Player({
              frames: this.frames,
              frameOffsets: this.frameOffsets,
              tmpCanvas: this.tmpCanvas,
              canvas: this.canvas,
              hasCanvasDom: this.options.hasCanvasDom,
              autoPlay: this.options.autoPlay,
              targetOffset: this.options.targetOffset,
              onClear: this.onClear.bind(this),
              onFrame: this.listener.progress,
              onFrameFinish: this.listener.finished,
            });
            player.init();
            return [2 /*return*/];
        }
      });
    });
  };
  GifToCanvas.prototype.on = function (event, fn) {
    this.listener[event] = fn;
  };
  /**
   * set upcanvas尺寸
   *
   * @memberof GifToCanvas
   */
  GifToCanvas.prototype.setCanvas = function () {
    var targetOffset = this.options.targetOffset;
    if (
      targetOffset === null || targetOffset === void 0
        ? void 0
        : targetOffset.width
    ) {
      var l = this.hdr.width / targetOffset.width;
      this.options.targetOffset = __assign(__assign({}, targetOffset), {
        dx: targetOffset.dx * l,
        dy: targetOffset.dy * l,
        sWidth: targetOffset.sWidth * l,
        sHeight: targetOffset.sHeight * l,
      });
      this.canvas.width = this.options.targetOffset.sWidth;
      this.canvas.height = this.options.targetOffset.sHeight;
    }
    this.tmpCanvas.width = this.hdr.width;
    this.tmpCanvas.height = this.hdr.height;
  };
  /**
   * 清除Dom节点
   *
   * @memberof GifToCanvas
   */
  GifToCanvas.prototype.onClear = function () {
    var _a, _b, _c, _d, _e;
    (_a = this.tmpCanvas.getContext("2d")) === null || _a === void 0
      ? void 0
      : _a.clearRect(0, 0, this.tmpCanvas.width, this.tmpCanvas.height);
    (_c =
      (_b = this.canvas) === null || _b === void 0
        ? void 0
        : _b.getContext("2d")) === null || _c === void 0
      ? void 0
      : _c.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.frames = [];
    this.clear();
    if (this.options.clear) {
      (_e =
        (_d = this.canvas) === null || _d === void 0
          ? void 0
          : _d.parentNode) === null || _e === void 0
        ? void 0
        : _e.removeChild(this.canvas);
    }
  };
  /**
   * Get Gif Data
   *
   * @param {string} url
   * @returns
   * @memberof GifToCanvas
   */
  GifToCanvas.prototype.createXhr = function (url) {
    return new Promise(function (resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.overrideMimeType("text/plain; charset=x-user-defined");
      xhr.withCredentials = false;
      xhr.onload = function (e) {
        if (e.target.status !== 200 && e.target.status !== 304) {
          reject("Status Error: " + e.target.status);
          return;
        }
        var data = e.target.response;
        if (data.toString().indexOf("ArrayBuffer") > 0) {
          data = new Uint8Array(data);
        }
        resolve(data);
      };
      xhr.onerror = function (e) {
        reject(e);
      };
      xhr.send();
    });
  };
  GifToCanvas.prototype.clear = function () {
    this.transparency = null;
    this.delay = null;
    this.lastDisposalMethod = this.disposalMethod;
    this.disposalMethod = null;
    this.frame = null;
  };
  GifToCanvas.prototype.pushFrame = function () {
    if (!this.frame) return;
    this.frames.push({
      data: this.frame.getImageData(0, 0, this.hdr.width, this.hdr.height),
      delay: this.delay,
    });
    this.frameOffsets.push({ x: 0, y: 0 });
  };
  GifToCanvas.prototype.doHdr = function (hdr) {
    this.hdr = hdr;
    this.setCanvas();
  };
  GifToCanvas.prototype.doGCE = function (gce) {
    this.pushFrame();
    this.clear();
    this.transparency = gce.transparencyGiven ? gce.transparencyIndex : null;
    this.delay = gce.delayTime;
    this.disposalMethod = gce.disposalMethod;
  };
  GifToCanvas.prototype.doNothing = function () {
    return null;
  };
  GifToCanvas.prototype.doImg = function (img) {
    var _this = this;
    if (!this.frame) this.frame = this.tmpCanvas.getContext("2d");
    if (!this.frame) return;
    var currIdx = this.frames.length;
    //ct = color table, gct = global color table
    var ct = img.lctFlag ? img.lct : this.hdr.gct; // TODO: What if neither exists?
    /*
            Disposal method indicates the way in which the graphic is to
            be treated after being displayed.
    
            Values :    0 - No disposal specified. The decoder is
                            not required to take any action.
                        1 - Do not dispose. The graphic is to be left
                            in place.
                        2 - Restore to background color. The area used by the
                            graphic must be restored to the background color.
                        3 - Restore to previous. The decoder is required to
                            restore the area overwritten by the graphic with
                            what was there prior to rendering the graphic.
    
                            Importantly, "previous" means the frame state
                            after the last disposal of method 0, 1, or 2.
            */
    if (currIdx > 0) {
      if (this.lastDisposalMethod === 3) {
        // Restore to previous
        // If we disposed every frame including first frame up to this point, then we have
        // no composited frame to restore to. In this case, restore to background instead.
        if (this.disposalRestoreFromIdx !== null) {
          this.frame.putImageData(
            this.frames[this.disposalRestoreFromIdx].data,
            0,
            0
          );
        } else {
          if (this.lastImg) {
            this.frame.clearRect(
              this.lastImg.leftPos,
              this.lastImg.topPos,
              this.lastImg.width,
              this.lastImg.height
            );
            // this.frame.clearRect(
            //   0,
            //   0,
            //   this.tmpCanvas.width,
            //   this.tmpCanvas.height
            // )
          }
        }
      } else {
        this.disposalRestoreFromIdx = currIdx - 1;
      }
      if (this.lastDisposalMethod === 2) {
        // Restore to background color
        // Browser implementations historically restore to transparent; we do the same.
        // http://www.wizards-toolkit.org/discourse-server/viewtopic.php?f=1&t=21172#p86079
        if (this.lastImg) {
          this.frame.clearRect(
            this.lastImg.leftPos,
            this.lastImg.topPos,
            this.lastImg.width,
            this.lastImg.height
          );
          // this.frame.clearRect(
          //   0,
          //   0,
          //   this.tmpCanvas.width,
          //   this.tmpCanvas.height
          // )
        }
      }
    }
    // else, Undefined/Do not dispose.
    // frame contains final pixel data from the last frame; do nothing
    //Get existing pixels for img region after applying disposal method
    var imgData = this.frame.getImageData(
      img.leftPos,
      img.topPos,
      img.width,
      img.height
    );
    //apply color table colors
    img.pixels.forEach(function (pixel, i) {
      // imgData.data === [R,G,B,A,R,G,B,A,...]
      if (pixel !== _this.transparency) {
        imgData.data[i * 4 + 0] = ct[pixel][0];
        imgData.data[i * 4 + 1] = ct[pixel][1];
        imgData.data[i * 4 + 2] = ct[pixel][2];
        imgData.data[i * 4 + 3] = 255; // Opaque.
      }
    });
    this.frame.putImageData(imgData, img.leftPos, img.topPos);
    // We could use the on-page canvas directly, except that we draw a progress
    // bar for each image chunk (not just the final image).
    // if (drawWhileLoading) {
    //   ctx.drawImage(tmpCanvas, 0, 0)
    //   drawWhileLoading = options.auto_play
    // }
    this.lastImg = img;
  };
  GifToCanvas.prototype.createHandle = function () {
    var _this = this;
    var withProgress = function (fn) {
      return function (block) {
        fn.call(_this, block);
      };
    };
    return {
      hdr: withProgress(this.doHdr),
      gce: withProgress(this.doGCE),
      // I guess that's all for now.
      img: withProgress(this.doImg),
      com: withProgress(this.doNothing),
      app: {
        NETSCAPE: withProgress(this.doNothing),
      },
      eof: function () {
        _this.pushFrame();
      },
    };
  };
  return GifToCanvas;
})();

// export default GifToCanvas;
// exports.GifToCanvas = GifToCanvas;
