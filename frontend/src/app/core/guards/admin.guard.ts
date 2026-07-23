import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Store } from '@ngxs/store';
import { AuthState } from '@core/state/auth.state';

export const adminGuard: CanActivateFn = () => {
  const store = inject(Store);
  const router = inject(Router);

  if (!store.selectSnapshot(AuthState.isAuthenticated)) {
    return router.createUrlTree(['/login']);
  }

  if (store.selectSnapshot(AuthState.isStaffOrAdmin)) {
    return true;
  }

  return router.createUrlTree(['/']);
};
