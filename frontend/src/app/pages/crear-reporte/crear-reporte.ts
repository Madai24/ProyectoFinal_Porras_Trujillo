import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ReportesService } from '../../services/reportes';
import { CatalogosService } from '../../services/catalogos';
import { NotificacionesService } from '../../services/notificaciones';
import { mensajeError } from '../../utils/errores';
import { Catalogo, NivelGravedad } from '../../models/huellas.models';

const TIPOS_IMAGEN = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_MB = 5;

@Component({
  selector: 'app-crear-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './crear-reporte.html',
  styleUrl: './crear-reporte.css'
})
export class CrearReporte implements OnInit {
  private reportesService = inject(ReportesService);
  private catalogosService = inject(CatalogosService);
  private notificaciones = inject(NotificacionesService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  distritos: Catalogo[] = [];
  tiposResiduo: Catalogo[] = [];

  direccion = '';
  referencia = '';
  nivel_gravedad: NivelGravedad = 'Media';
  toneladas = 0;
  distrito_id?: number;
  tipo_residuo_id?: number;
  archivoSeleccionado: File | null = null;

  cargando = false;
  error = '';

  ngOnInit(): void {
    this.catalogosService.getDistritos().subscribe({
      next: (d) => {
        this.distritos = d;
        this.cdr.markForCheck();
      },
      error: (err) => this.notificaciones.error(mensajeError(err, 'No se pudieron cargar los distritos.'))
    });
    this.catalogosService.getTiposResiduo().subscribe({
      next: (t) => {
        this.tiposResiduo = t;
        this.cdr.markForCheck();
      },
      error: (err) => this.notificaciones.error(mensajeError(err, 'No se pudieron cargar los tipos de residuo.'))
    });
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const archivo = input.files?.[0] ?? null;
    if (!archivo) {
      this.archivoSeleccionado = null;
      return;
    }
    if (!TIPOS_IMAGEN.includes(archivo.type)) {
      this.notificaciones.error('La foto debe ser JPG, PNG o WebP.');
      input.value = '';
      this.archivoSeleccionado = null;
      return;
    }
    if (archivo.size > MAX_MB * 1024 * 1024) {
      this.notificaciones.error(`La foto pesa demasiado. El máximo es ${MAX_MB} MB.`);
      input.value = '';
      this.archivoSeleccionado = null;
      return;
    }
    this.archivoSeleccionado = archivo;
  }

  private validar(): string {
    if (this.direccion.trim().length < 5) return 'Escribe la dirección exacta (mínimo 5 caracteres).';
    if (!this.distrito_id) return 'Selecciona un distrito.';
    if (!this.tipo_residuo_id) return 'Selecciona un tipo de residuo.';
    if (this.toneladas < 0 || this.toneladas > 9999.99) return 'Las toneladas estimadas deben estar entre 0 y 9999.99.';
    return '';
  }

  enviarReporte() {
    const problema = this.validar();
    if (problema) {
      this.error = problema;
      this.notificaciones.error(problema);
      return;
    }

    this.cargando = true;
    this.error = '';

    const formData = new FormData();
    formData.append('direccion', this.direccion.trim());
    if (this.referencia.trim()) formData.append('referencia_visual', this.referencia.trim());
    formData.append('nivel_urgencia', this.nivel_gravedad);
    formData.append('distrito_id', String(this.distrito_id));
    formData.append('tipo_residuo_id', String(this.tipo_residuo_id));
    formData.append('toneladas_estimadas', String(this.toneladas || 0));
    if (this.archivoSeleccionado) {
      formData.append('archivo', this.archivoSeleccionado);
    }

    this.reportesService.crear(formData).subscribe({
      next: () => {
        this.cargando = false;
        this.cdr.markForCheck();
        this.notificaciones.exito('¡Reporte registrado correctamente!');
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.status === 401
          ? 'Debes iniciar sesión para crear un reporte.'
          : mensajeError(err, 'No se pudo crear el reporte.');
        this.cdr.markForCheck();
        this.notificaciones.error(this.error);
      }
    });
  }
}
