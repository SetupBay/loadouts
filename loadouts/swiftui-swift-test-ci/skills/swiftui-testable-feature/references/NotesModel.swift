import Foundation
import Observation

/// View state for the notes screen. Owns no SwiftUI types, so it builds and tests on Linux.
@MainActor
@Observable
public final class NotesModel {
    public enum State: Equatable {
        case idle
        case loading
        case loaded([Note])
        case failed(String)
    }

    public private(set) var state: State = .idle
    public var searchText = ""

    private let client: any NotesClient
    private let now: @Sendable () -> Date

    public init(client: any NotesClient, now: @escaping @Sendable () -> Date = Date.init) {
        self.client = client
        self.now = now
    }

    /// Notes to show: newest first, filtered by the search text (title or body, case-insensitive).
    public var visibleNotes: [Note] {
        guard case .loaded(let notes) = state else { return [] }
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        let filtered =
            query.isEmpty
            ? notes
            : notes.filter { $0.title.localizedCaseInsensitiveContains(query) || $0.body.localizedCaseInsensitiveContains(query) }
        return filtered.sorted { $0.updatedAt > $1.updatedAt }
    }

    public func load() async {
        if case .loading = state { return }
        state = .loading
        do {
            state = .loaded(try await client.fetchNotes())
        } catch {
            state = .failed(Self.message(for: error))
        }
    }

    /// Validates, saves through the client, and replaces or appends the saved note.
    public func save(title: String, body: String, id: UUID? = nil) async throws {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, trimmed.count <= 120 else { throw NotesError.invalidTitle }
        let saved = try await client.save(Note(id: id ?? UUID(), title: trimmed, body: body, updatedAt: now()))
        guard case .loaded(var notes) = state else {
            state = .loaded([saved])
            return
        }
        if let index = notes.firstIndex(where: { $0.id == saved.id }) {
            notes[index] = saved
        } else {
            notes.append(saved)
        }
        state = .loaded(notes)
    }

    static func message(for error: any Error) -> String {
        switch error {
        case NotesError.offline: "You're offline. Pull to try again."
        case NotesError.server(let status): "The server returned an error (\(status))."
        default: "Something went wrong."
        }
    }
}
