import { Component, inject } from '@angular/core';
import { RouterOutlet, RouterLink, Router } from '@angular/router';
import { AuthService } from './services/auth';
import { NotificacionesService } from './services/notificaciones';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  authService = inject(AuthService);
  notificaciones = inject(NotificacionesService);
  private router = inject(Router);

  salir() {
    this.authService.cerrarSesion();
    this.notificaciones.info('Sesión cerrada.');
    this.router.navigate(['/login']);
  }
}