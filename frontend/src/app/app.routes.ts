import { Routes } from '@angular/router';
import { Dashboard } from './pages/dashboard/dashboard';
import { Login } from './pages/login/login';
import { Registro } from './pages/registro/registro';
import { CrearReporte } from './pages/crear-reporte/crear-reporte';
import { DetalleReporte } from './pages/detalle-reporte/detalle-reporte';
import { Perfil } from './pages/perfil/perfil';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'login', component: Login },
  { path: 'registro', component: Registro },
  { path: 'nuevo-reporte', component: CrearReporte },
  { path: 'reporte/:id', component: DetalleReporte },
  { path: 'perfil', component: Perfil },
  { path: '**', redirectTo: '' }
];