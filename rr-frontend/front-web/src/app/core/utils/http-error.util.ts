import { HttpErrorResponse } from '@angular/common/http';

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof HttpErrorResponse) {
    if (isParsingFailure(error)) {
      return fallback;
    }

    if (typeof error.error === 'string') {
      const apiMessage = getDisplayableMessage(error.error);
      if (apiMessage) {
        return apiMessage;
      }
    }

    if (isRecord(error.error)) {
      const apiError = error.error['error'];
      if (typeof apiError === 'string') {
        const apiMessage = getDisplayableMessage(apiError);
        if (apiMessage) {
          return apiMessage;
        }
      }

      for (const value of Object.values(error.error)) {
        if (typeof value === 'string') {
          const apiMessage = getDisplayableMessage(value);
          if (apiMessage) {
            return apiMessage;
          }
        }

        if (Array.isArray(value) && typeof value[0] === 'string') {
          const apiMessage = getDisplayableMessage(value[0]);
          if (apiMessage) {
            return apiMessage;
          }
        }
      }
    }

    const httpMessage = getDisplayableMessage(error.message);
    if (httpMessage) {
      return httpMessage;
    }
  }

  if (error instanceof Error) {
    const errorMessage = getDisplayableMessage(error.message);
    if (errorMessage) {
      return errorMessage;
    }
  }

  return fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getDisplayableMessage(message: string): string | null {
  const trimmedMessage = message.trim();

  if (!trimmedMessage || looksLikeHtml(trimmedMessage)) {
    return null;
  }

  return trimmedMessage;
}

function looksLikeHtml(value: string): boolean {
  const normalizedValue = value.trim().toLowerCase();

  return normalizedValue.startsWith('<!doctype html') || normalizedValue.startsWith('<html');
}

function isParsingFailure(error: HttpErrorResponse): boolean {
  const normalizedMessage = error.message.trim().toLowerCase();

  return normalizedMessage.startsWith('http failure during parsing');
}