// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "NotesCore",
    platforms: [.iOS(.v18), .macOS(.v15)],
    products: [
        .library(name: "NotesCore", targets: ["NotesCore"])
    ],
    targets: [
        .target(name: "NotesCore"),
        .testTarget(name: "NotesCoreTests", dependencies: ["NotesCore"]),
    ],
    swiftLanguageModes: [.v6]
)
