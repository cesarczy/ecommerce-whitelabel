import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideStore } from '@ngxs/store';

import { routes } from './app.routes';
import { authInterceptor } from '@core/interceptors/auth.interceptor';
import { AuthState } from '@core/state/auth.state';
import { CartState } from '@core/state/cart.state';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
    provideStore([AuthState, CartState]),
  ],
};
