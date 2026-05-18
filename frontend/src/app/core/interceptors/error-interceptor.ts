import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { UiService } from '../services/ui.service';

function extractMessage(err: HttpErrorResponse): string {
  const body = err.error;
  if (!body) {
    return err.message || 'Request failed.';
  }
  if (typeof body === 'string') {
    return body;
  }
  if (body.message) {
    return body.message;
  }
  if (body.detail) {
    return typeof body.detail === 'string' ? body.detail : String(body.detail);
  }
  if (body.error && typeof body.error === 'string') {
    return body.error;
  }
  return err.message || 'Request failed.';
}

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const ui = inject(UiService);

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401 || err.status === 0) {
        return throwError(() => err);
      }
      if (err.status >= 500) {
        ui.showError(extractMessage(err));
      }
      return throwError(() => err);
    }),
  );
};
