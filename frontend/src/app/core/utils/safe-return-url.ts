/** Allow only same-origin relative paths for post-login redirects. */
export function safeReturnUrl(raw: string | null | undefined): string | null {
  if (!raw || typeof raw !== 'string') {
    return null;
  }
  const path = raw.trim();
  if (!path.startsWith('/') || path.startsWith('//')) {
    return null;
  }
  return path;
}
