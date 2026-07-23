import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngxs/store';
import { AuthState } from '@core/state/auth.state';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const store = inject(Store);
  const token = store.selectSnapshot(AuthState.accessToken);
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }
  return next(req);
};
