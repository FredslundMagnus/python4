/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
import { 
  createConnection, 
  TextDocuments, 
  Diagnostic, 
  DiagnosticSeverity, 
  ProposedFeatures, 
  InitializeParams, 
  DidChangeConfigurationNotification, 
  CompletionItem, 
  CompletionItemKind, 
  TextDocumentPositionParams, 
  TextDocumentSyncKind, 
  InitializeResult, 
  Hover, 
  MarkupKind,
  SymbolInformation,
  DocumentSymbolParams,
  SymbolKind,
  DocumentHighlight,
  DocumentHighlightKind,
  DocumentHighlightParams,
  CodeAction,
  CodeActionParams,
  DefinitionParams,
  Definition,
  DocumentColorParams,
  ColorInformation,
  ColorPresentationParams,
  ColorPresentation,
  SignatureHelp,
  SignatureHelpParams,
  WorkspaceSymbolParams,
  DocumentSymbol,
} from "vscode-languageserver/node";
// ignore typescript error


const selector = { language: 'java', scheme: 'file' }; // register for all Java documents from the local file system


import { TextDocument } from "vscode-languageserver-textdocument";
// import { DocumentSymbol } from 'vscode-languageserver';



// Create a connection for the server, using Node's IPC as a transport.
// Also include all preview / proposed LSP features.
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager.
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let hasConfigurationCapability = false;
let hasWorkspaceFolderCapability = false;
let hasDiagnosticRelatedInformationCapability = false;

import fs = require("fs");
import tmp = require("tmp");
import path = require("path");

import util = require("node:util");
import { TextEncoder } from "node:util";
import { fileURLToPath } from "node:url";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const exec = util.promisify(require("node:child_process").exec);

connection.onInitialize((params: InitializeParams) => {
  const capabilities = params.capabilities;

  // Does the client support the `workspace/configuration` request?
  // If not, we fall back using global settings.
  hasConfigurationCapability = !!(capabilities.workspace && !!capabilities.workspace.configuration);
  hasWorkspaceFolderCapability = !!(capabilities.workspace && !!capabilities.workspace.workspaceFolders);
  hasDiagnosticRelatedInformationCapability = !!(capabilities.textDocument && capabilities.textDocument.publishDiagnostics && capabilities.textDocument.publishDiagnostics.relatedInformation);

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      // Tell the client that this server supports code completion.
      completionProvider: {
        resolveProvider: true,
      },
      hoverProvider: true,
      documentSymbolProvider: true,
      documentHighlightProvider: true,
      codeActionProvider: true,
      semanticTokensProvider: {
        legend: {
          tokenTypes: [
            "comment",
            "keyword",
            "string",
            "number",
            "regexp",
            "operator",
            "namespace",
            "type",
            "struct",
            "class",
            "interface",
            "enum",
            "typeParameter",
            "function",
            "member",
            "macro",
            "variable",
            "parameter",
            "property",
            "label",
          ],
          tokenModifiers: [
            "declaration",
            "documentation",
            "static",
            "abstract",
            "deprecated",
            "modification",
            "async",
          ],
        },
        // range: true,
        // full: {
        //   delta: true,
        // },
      },
      workspaceSymbolProvider: true,
      definitionProvider: true,
      colorProvider: true,
      signatureHelpProvider: {
        triggerCharacters: ["(", ","],
      },

    },
  };
  if (hasWorkspaceFolderCapability) {
    result.capabilities.workspace = {
      workspaceFolders: {
        supported: true,
      },
    };
  }
  return result;
});

connection.onInitialized(() => {
  if (hasConfigurationCapability) {
    // Register for all configuration changes.
    connection.client.register(DidChangeConfigurationNotification.type, undefined);
  }
  if (hasWorkspaceFolderCapability) {
    connection.workspace.onDidChangeWorkspaceFolders((_event) => {
      connection.console.log("Workspace folder change event received.");
    });
  }
});

// The example settings
interface ExampleSettings {
  maxNumberOfProblems: number;
}

// The global settings, used when the `workspace/configuration` request is not supported by the client.
// Please note that this is not the case when using this server with the client provided in this example
// but could happen with other clients.
const defaultSettings: ExampleSettings = { maxNumberOfProblems: 1000 };
let globalSettings: ExampleSettings = defaultSettings;

// Cache the settings of all open documents
const documentSettings: Map<string, Thenable<ExampleSettings>> = new Map();

connection.onDidChangeConfiguration((change) => {
  if (hasConfigurationCapability) {
    // Reset all cached document settings
    documentSettings.clear();
  } else {
    globalSettings = <ExampleSettings>(change.settings.languageServerExample || defaultSettings);
  }

  // Revalidate all open text documents
  documents.all().forEach(validateTextDocument);
});

function getDocumentSettings(resource: string): Thenable<ExampleSettings> {
  if (!hasConfigurationCapability) {
    return Promise.resolve(globalSettings);
  }
  let result = documentSettings.get(resource);
  if (!result) {
    result = connection.workspace.getConfiguration({
      scopeUri: resource,
      section: "languageServerExample",
    });
    documentSettings.set(resource, result);
  }
  return result;
}

// Only keep settings for open documents
documents.onDidClose((e) => {
  documentSettings.delete(e.document.uri);
});

// The content of a text document has changed. This event is emitted
// when the text document first opened or when its content has changed.
documents.onDidChangeContent((change) => {
  validateTextDocument(change.document);
});

async function validateTextDocument(textDocument: TextDocument): Promise<void> {
  // In this simple example we get the settings for every validate run.
  const settings = await getDocumentSettings(textDocument.uri);

  // The validator creates diagnostics for all uppercase words length 2 and more
  const text = textDocument.getText();
  const pattern = /\b[A-Z]{2,}\b/g;
  let m: RegExpExecArray | null;

  let problems = 0;
  const diagnostics: Diagnostic[] = [];
  while ((m = pattern.exec(text)) && problems < (settings?.maxNumberOfProblems ?? 100)) {
    problems++;
    const diagnostic: Diagnostic = {
      severity: DiagnosticSeverity.Warning,
      range: {
        start: textDocument.positionAt(m.index),
        end: textDocument.positionAt(m.index + m[0].length),
      },
      message: `${m[0]} is all uppercase.`,
      source: "ex",
    };
    if (hasDiagnosticRelatedInformationCapability) {
      diagnostic.relatedInformation = [
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range),
          },
          message: "Spelling matters",
        },
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range),
          },
          message: "Particularly for names",
        },
      ];
    }
    diagnostics.push(diagnostic);
  }

  // Send the computed diagnostics to VSCode.
  connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });

}

connection.onDidChangeWatchedFiles((_change) => {
  // Monitored files have change in VSCode
  connection.console.log("We received an file change event");
});

// This handler provides the initial list of the completion items.
connection.onCompletion((_textDocumentPosition: TextDocumentPositionParams): CompletionItem[] => {
  // The pass parameter contains the position of the text document in
  // which code complete got requested. For the example we ignore this
  // info and always provide the same completion items.
  return [
    {
      label: "TypeScript",
      kind: CompletionItemKind.Text,
      data: 1,
    },
    {
      label: "JavaScript",
      kind: CompletionItemKind.Text,
      data: 2,
    },
  ];
});

// This handler resolves additional information for the item selected in
// the completion list.
connection.onCompletionResolve((item: CompletionItem): CompletionItem => {
  if (item.data === 1) {
    item.detail = "TypeScript details";
    item.documentation = "TypeScript documentation";
  } else if (item.data === 2) {
    item.detail = "JavaScript details";
    item.documentation = "JavaScript documentation";
  }
  return item;
});

connection.onDocumentSymbol((params: DocumentSymbolParams): DocumentSymbol[] => {
  return [
    {
      name: "int",
      detail: "int",
      kind: SymbolKind.Variable,
      range: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 3 },
      },
      selectionRange: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 3 },
      },
    },
  ];
});

connection.onColorPresentation((params: ColorPresentationParams): ColorPresentation[] => {
  return [
    {
      label: "Color Presentation",
      textEdit: {
        range: params.range,
        newText: "Color Presentation",
      },
    },
  ];
});

connection.onWorkspaceSymbol((params: WorkspaceSymbolParams): SymbolInformation[] => {
  return [
    {
      name: "int",
      kind: SymbolKind.Class,
      location: {
        uri: params.query,
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 3 },
        },
      },
    },
  ];
});

connection.onDocumentHighlight((params: DocumentHighlightParams): DocumentHighlight[] => {
  return [
    {

      range: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 3 },
      },
      kind: DocumentHighlightKind.Write,
    },
  ];
});

connection.onDefinition((params: DefinitionParams): Definition => {
  return {
    uri: params.textDocument.uri,
    range: {
      start: { line: 0, character: 0 },
      end: { line: 0, character: 3 },
    },
  };
});

connection.onCodeAction((params: CodeActionParams): CodeAction[] => {
  return [
    {
      title: "Code Action",
      command: {
        title: "Code Action",
        command: "example.codeAction",
        arguments: [params.textDocument.uri, params.range],
      },
    },
  ];
});

connection.onCodeActionResolve((codeAction: CodeAction): CodeAction => {
  return codeAction;
});

connection.onHover((_textDocumentPosition: TextDocumentPositionParams): Hover => {
  // _textDocumentPosition.position.character
  return {
    contents: {
      language: MarkupKind.Markdown,
      value: [
		'int'
	].join('\n'),
    },
  };
});

// add syntax highlighting
connection.onDocumentColor((params: DocumentColorParams): ColorInformation[] => {
  return [
    {
      color: { red: 1, green: 0, blue: 0, alpha: 1 },
      range: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 3 },
      },
    },
  ];
});

connection.onColorPresentation((params: ColorPresentationParams): ColorPresentation[] => {
  return [
    {
      label: "red",
      textEdit: {
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 3 },
        },
        newText: "red",
      },
    },
  ];
});

connection.onSignatureHelp((params: SignatureHelpParams): SignatureHelp => {
  return {
    signatures: [
      {
        label: "(a: int, b: float) -> str",
        parameters: [
          {
            label: "a: int",
          },
          {
            label: "b: float",
          },
        ],
        activeParameter: 0,
      },
    ],
    activeSignature: 0,
    activeParameter: 0,
  };
});


// Make the text document manager listen on the connection
// for open, change and close text document events
documents.listen(connection);

// Listen on the connection
connection.listen();

