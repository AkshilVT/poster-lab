// cutout — lift the foreground subject(s) out of a photo with Apple Vision
// (the same model behind "Copy Subject" in Photos). macOS 14+.
//
//   cutout <in> <out.png> [--mask <mask.png>] [--each <dir>]
//
// <out.png>  the photo with every subject kept and the rest transparent
// --mask     the soft 0..255 foreground mask at full image size
// --each     one mask per detected instance: <dir>/inst-<n>.png
// stdout     {"instances": n, "w": px, "h": px}
import CoreImage
import CoreImage.CIFilterBuiltins
import Foundation
import Vision

func fail(_ msg: String, _ code: Int32 = 1) -> Never {
  FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
  exit(code)
}

let args = CommandLine.arguments
guard args.count >= 3 else { fail("usage: cutout <in> <out.png> [--mask <mask.png>] [--each <dir>]") }
let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
var maskURL: URL?
var eachDir: URL?
var i = 3
while i + 1 < args.count {
  switch args[i] {
  case "--mask": maskURL = URL(fileURLWithPath: args[i + 1])
  case "--each": eachDir = URL(fileURLWithPath: args[i + 1], isDirectory: true)
  default: fail("unknown option \(args[i])")
  }
  i += 2
}

guard let image = CIImage(contentsOf: inURL, options: [.applyOrientationProperty: true]) else {
  fail("cannot read \(inURL.path)")
}
let handler = VNImageRequestHandler(ciImage: image, options: [:])
let request = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([request]) } catch { fail("vision failed: \(error)") }
guard let observation = request.results?.first, !observation.allInstances.isEmpty else {
  fail("no subject found", 3)
}

let context = CIContext()
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let gray = CGColorSpace(name: CGColorSpace.linearGray)!

func mask(_ instances: IndexSet) -> CIImage {
  do {
    let buffer = try observation.generateScaledMaskForImage(forInstances: instances, from: handler)
    return CIImage(cvPixelBuffer: buffer)
  } catch { fail("mask failed: \(error)") }
}

let all = observation.allInstances
let full = mask(all)
let blend = CIFilter.blendWithMask()
blend.inputImage = image
blend.backgroundImage = CIImage.empty()
blend.maskImage = full
do {
  try context.writePNGRepresentation(
    of: blend.outputImage!.cropped(to: image.extent), to: outURL, format: .RGBA8, colorSpace: srgb)
  if let maskURL {
    try context.writePNGRepresentation(of: full, to: maskURL, format: .L8, colorSpace: gray)
  }
  if let eachDir {
    try FileManager.default.createDirectory(at: eachDir, withIntermediateDirectories: true)
    for n in all {
      let url = eachDir.appendingPathComponent("inst-\(n).png")
      try context.writePNGRepresentation(of: mask(IndexSet(integer: n)), to: url, format: .L8, colorSpace: gray)
    }
  }
} catch { fail("write failed: \(error)") }

print("{\"instances\": \(all.count), \"w\": \(Int(image.extent.width)), \"h\": \(Int(image.extent.height))}")
