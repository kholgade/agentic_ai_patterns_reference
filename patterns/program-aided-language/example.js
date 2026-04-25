export async function runPal(problem, codegenFn, execFn) {
  const code = await codegenFn(`Write JS code only to solve:\n${problem}`);
  const executionResult = await execFn(code);
  return { code, executionResult };
}
