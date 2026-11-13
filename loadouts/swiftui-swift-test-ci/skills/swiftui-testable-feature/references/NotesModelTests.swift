import Foundation
import Testing

@testable import NotesCore

/// Fake client: canned results, records saves. An actor, so it is Sendable without locks.
actor FakeNotesClient: NotesClient {
    var notes: [Note]
    var fetchError: NotesError?
    private(set) var saved: [Note] = []

    init(notes: [Note] = [], fetchError: NotesError? = nil) {
        self.notes = notes
        self.fetchError = fetchError
    }

    func fetchNotes() async throws -> [Note] {
        if let fetchError { throw fetchError }
        return notes
    }

    func save(_ note: Note) async throws -> Note {
        saved.append(note)
        return note
    }
}

let day: TimeInterval = 86_400
let fixed = Date(timeIntervalSince1970: 1_790_000_000)

func note(_ title: String, _ body: String = "", daysAgo: Double) -> Note {
    Note(title: title, body: body, updatedAt: fixed.addingTimeInterval(-daysAgo * day))
}

@MainActor
@Suite("NotesModel")
struct NotesModelTests {
    @Test("load shows notes newest first")
    func loadSortsNewestFirst() async {
        let client = FakeNotesClient(notes: [note("Old", daysAgo: 3), note("New", daysAgo: 0), note("Mid", daysAgo: 1)])
        let model = NotesModel(client: client, now: { fixed })
        await model.load()
        #expect(model.visibleNotes.map(\.title) == ["New", "Mid", "Old"])
    }

    @Test(
        "a failed load shows a message, not an empty list",
        arguments: [
            (NotesError.offline, "You're offline. Pull to try again."),
            (NotesError.server(status: 503), "The server returned an error (503)."),
        ])
    func loadFailure(error: NotesError, message: String) async {
        let model = NotesModel(client: FakeNotesClient(fetchError: error), now: { fixed })
        await model.load()
        #expect(model.state == .failed(message))
        #expect(model.visibleNotes.isEmpty)
    }

    @Test("search matches title or body, case-insensitively, ignoring spaces")
    func search() async {
        let client = FakeNotesClient(notes: [
            note("Groceries", "milk, eggs", daysAgo: 0), note("Ideas", "Buy MILK frother", daysAgo: 1), note("Trip", daysAgo: 2),
        ])
        let model = NotesModel(client: client, now: { fixed })
        await model.load()
        model.searchText = "  milk "
        #expect(model.visibleNotes.map(\.title) == ["Groceries", "Ideas"])
    }

    @Test("save trims the title, stamps the time and appends")
    func saveAppends() async throws {
        let client = FakeNotesClient(notes: [note("First", daysAgo: 1)])
        let model = NotesModel(client: client, now: { fixed })
        await model.load()
        try await model.save(title: "  Second  ", body: "b")
        #expect(model.visibleNotes.map(\.title) == ["Second", "First"])
        let saved = await client.saved
        #expect(saved.count == 1)
        #expect(saved.first?.updatedAt == fixed)
    }

    @Test("save with an existing id replaces that note")
    func saveReplaces() async throws {
        let existing = note("Draft", daysAgo: 2)
        let model = NotesModel(client: FakeNotesClient(notes: [existing]), now: { fixed })
        await model.load()
        try await model.save(title: "Final", body: "done", id: existing.id)
        #expect(model.visibleNotes.count == 1)
        #expect(model.visibleNotes.first?.title == "Final")
    }

    @Test("blank or over-long titles are rejected before the client is called", arguments: ["", "   ", String(repeating: "x", count: 121)])
    func invalidTitle(title: String) async {
        let client = FakeNotesClient()
        let model = NotesModel(client: client, now: { fixed })
        await #expect(throws: NotesError.invalidTitle) {
            try await model.save(title: title, body: "")
        }
        #expect(await client.saved.isEmpty)
    }
}
