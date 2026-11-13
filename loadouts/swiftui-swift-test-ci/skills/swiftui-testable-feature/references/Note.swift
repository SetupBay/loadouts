import Foundation

public struct Note: Identifiable, Equatable, Sendable, Codable {
    public let id: UUID
    public var title: String
    public var body: String
    public var updatedAt: Date

    public init(id: UUID = UUID(), title: String, body: String, updatedAt: Date) {
        self.id = id
        self.title = title
        self.body = body
        self.updatedAt = updatedAt
    }
}

/// The only way the view model reaches the network or disk. Tests pass a fake.
public protocol NotesClient: Sendable {
    func fetchNotes() async throws -> [Note]
    func save(_ note: Note) async throws -> Note
}

public enum NotesError: Error, Equatable, Sendable {
    case offline
    case server(status: Int)
    case invalidTitle
}
