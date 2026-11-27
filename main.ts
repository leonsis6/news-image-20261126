// main.ts — news-image-20261126 entry (Node 22, standard library only).
//
// Copies the pre-rendered entry.png beside this file to $MAKEFUN_OUTPUT_DIR
// (default /output), after validating that it is a whole 1024x1024 PNG:
// correct PNG signature, an IHDR chunk declaring 1024x1024, every chunk's
// CRC intact, and a trailing IEND chunk with nothing after it. A truncated
// or corrupt file is refused with a non-zero exit instead of being copied.
// Deterministic: the same input bytes produce the same output bytes.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const SRC = join(dirname(fileURLToPath(import.meta.url)), "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const OUT = join(OUT_DIR, "entry.png");

const PNG_SIG = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);

function fail(msg: string): never {
  console.error(`main.ts: refusing to write entry: ${msg}`);
  process.exit(1);
}

// CRC-32 (PNG polynomial 0xEDB88320) over chunk type + data.
const CRC_TABLE: Uint32Array = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const b of buf) {
    c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

const data = readFileSync(SRC);

if (data.length < 8 || !data.subarray(0, 8).equals(PNG_SIG)) {
  fail("bad PNG signature");
}

let off = 8;
let sawIHDR = false;
let sawIEND = false;
let width = 0;
let height = 0;

while (off + 8 <= data.length) {
  const len = data.readUInt32BE(off);
  const type = data.toString("latin1", off + 4, off + 8);
  if (off + 12 + len > data.length) {
    fail(`truncated ${type} chunk`);
  }
  const chunkData = data.subarray(off + 8, off + 8 + len);
  const crcStored = data.readUInt32BE(off + 8 + len);
  const crcActual = crc32(
    Buffer.concat([Buffer.from(type, "latin1"), chunkData]),
  );
  if (crcActual !== crcStored) {
    fail(`bad CRC in ${type} chunk`);
  }
  if (type === "IHDR") {
    if (len !== 13) {
      fail("bad IHDR length");
    }
    width = chunkData.readUInt32BE(0);
    height = chunkData.readUInt32BE(4);
    sawIHDR = true;
  }
  if (type === "IEND") {
    if (len !== 0) {
      fail("bad IEND length");
    }
    sawIEND = true;
    off += 12 + len;
    break;
  }
  off += 12 + len;
}

if (!sawIHDR) {
  fail("no IHDR chunk");
}
if (!sawIEND) {
  fail("no IEND chunk — file is truncated");
}
if (off !== data.length) {
  fail("trailing bytes after IEND");
}
if (width !== 1024 || height !== 1024) {
  fail(`IHDR is ${width}x${height}, expected 1024x1024`);
}

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, data);
console.log(`main.ts: wrote ${OUT} (${data.length} bytes, 1024x1024 PNG)`);
