export function parseReceipt(text) {
  return {
    length: text.length,
    preview: text.slice(0, 50)
  };
}
