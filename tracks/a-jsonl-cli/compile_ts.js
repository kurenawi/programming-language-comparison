const ts = require('/tmp/lil-246/node_modules/typescript');
const config = {
  compilerOptions: {
    target: ts.ScriptTarget.ES2020,
    module: ts.ModuleKind.NodeNext,
    moduleResolution: ts.ModuleResolutionKind.NodeNext,
    outDir: '/tmp/lil-246/dist',
    strict: true,
    esModuleInterop: true,
    skipLibCheck: true,
    types: ['node'],
    typeRoots: ['/tmp/lil-246/node_modules/@types']
  },
  files: ['/tmp/lil-246/tasks_cli.ts']
};
const host = ts.createCompilerHost(config.compilerOptions);
const program = ts.createProgram(config.files, config.compilerOptions, host);
const result = program.emit();
const diagnostics = ts.getPreEmitDiagnostics(program).concat(result.diagnostics);
if (diagnostics.length) {
  for (const diagnostic of diagnostics) {
    const message = ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n');
    console.error(message);
  }
}
process.exit(result.emitSkipped ? 1 : 0);
