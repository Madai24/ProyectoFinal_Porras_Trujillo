import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ReportesService } from '../../services/reportes';
import { CatalogosService } from '../../services/catalogos';
import { Catalogo, NivelGravedad } from '../../models/huellas.models';

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
  private router = inject(Router);

  distritos: Catalogo[] = [];
  tiposResiduo: Catalogo[] = [];

  titulo = '';
  descripcion = '';
  direccion = '';
  referencia = '';
  nivel_gravedad: NivelGravedad = 'Media';
  distrito_id?: number;
  tipo_residuo_id?: number;
  archivoSeleccionado: File | null = null;

  cargando = false;
  error = '';

  ngOnInit(): void {
    this.catalogosService.getDistritos().subscribe(d => this.distritos = d);
    this.catalogosService.getTiposResiduo().subscribe(t => this.tiposResiduo = t);
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.archivoSeleccionado = input.files[0];
    }
  }

  enviarReporte() {
    if (!this.distrito_id || !this.tipo_residuo_id) {
      this.error = 'Selecciona un distrito y un tipo de residuo.';
      return;
    }

    this.cargando = true;
    this.error = '';

    const formData = new FormData();
    formData.append('titulo', this.titulo);
    formData.append('descripcion', this.descripcion);
    formData.append('direccion', this.direccion);
    formData.append('referencia', this.referencia);
    formData.append('nivel_gravedad', this.nivel_gravedad);
    formData.append('distrito_id', String(this.distrito_id));
    formData.append('tipo_residuo_id', String(this.tipo_residuo_id));
    if (this.archivoSeleccionado) {
      formData.append('archivo', this.archivoSeleccionado);
    }

    this.reportesService.crear(formData).subscribe({
      next: () => {
        alert('¡Reporte registrado correctamente!');
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'No se pudo crear el reporte. Verifica que hayas iniciado sesión.';
      }
    });
  }
}