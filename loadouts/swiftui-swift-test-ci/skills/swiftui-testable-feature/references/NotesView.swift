#if canImport(SwiftUI)
import SwiftUI

/// Thin view: reads model state, forwards user intent. No logic worth testing lives here.
public struct NotesView: View {
    @State private var model: NotesModel

    public init(model: NotesModel) {
        _model = State(initialValue: model)
    }

    public var body: some View {
        NavigationStack {
            content
                .navigationTitle("Notes")
                .searchable(text: $model.searchText)
                .refreshable { await model.load() }
                .task { await model.load() }
        }
    }

    @ViewBuilder private var content: some View {
        switch model.state {
        case .idle, .loading:
            ProgressView()
        case .failed(let message):
            ContentUnavailableView("Couldn't load notes", systemImage: "wifi.slash", description: Text(message))
        case .loaded:
            List(model.visibleNotes) { note in
                VStack(alignment: .leading) {
                    Text(note.title).font(.headline)
                    Text(note.body).font(.subheadline).lineLimit(2)
                }
            }
        }
    }
}
#endif
