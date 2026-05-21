import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormControl, Validators, AbstractControl } from '@angular/forms';
import { Resource, ResourceLabel, RESOURCE_LABEL_DISPLAY, Category, Relation } from '../../../core/models/resource.model';
import { ResourceService } from '../services/resource.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-resource-form',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule],
  templateUrl: './resource-form.html',
})
export class ResourceForm implements OnInit {
  private readonly fb      = inject(FormBuilder);
  private readonly route   = inject(ActivatedRoute);
  private readonly router  = inject(Router);
  private readonly service = inject(ResourceService);
  private readonly api     = inject(ApiService);

  isEdit     = false;
  resourceId = '';
  loading    = signal(false);
  error      = signal<string | null>(null);
  categories = signal<Category[]>([]);
  relations  = signal<Relation[]>([]);

  readonly labelOptions = Object.entries(RESOURCE_LABEL_DISPLAY) as [ResourceLabel, string][];

  private static minOne(control: AbstractControl) {
    return (control.value as string[]).length > 0 ? null : { minOne: true };
  }

  readonly form = this.fb.group({
    resource_title:       ['', [Validators.required, Validators.maxLength(255)]],
    resource_description: [''],
    resource_label:       ['', Validators.required],
    categories:           new FormControl<string[]>([], { nonNullable: true, validators: ResourceForm.minOne }),
    relations:            new FormControl<string[]>([], { nonNullable: true, validators: ResourceForm.minOne }),
    // reading_sheet
    book_title:           [''],
    book_author:          [''],
    summary:              [''],
    // games
    game_url:             [''],
    game_platform:        [''],
    game_instructions:    [''],
    // videos
    video_url:            [''],
    video_duration:       [null as number | null],
    video_platform:       [''],
    // pdf
    pdf_url:              [''],
    pdf_publisher:        [''],
    pdf_page_count:       [null as number | null],
    // activity
    activity_instructions:       [''],
    activity_duration:           [null as number | null],
    activity_required_materials: [''],
    // article
    article_url:          [''],
    article_publisher:    [''],
    // challenge_card
    challenge_card_duration: [null as number | null],
    // exercise
    exercise_instructions: [''],
    exercise_duration:     [null as number | null],
  });

  get selectedLabel(): string {
    return this.form.get('resource_label')!.value ?? '';
  }

  get selectedCategories(): string[] {
    return this.form.get('categories')!.value ?? [];
  }

  get selectedRelations(): string[] {
    return this.form.get('relations')!.value ?? [];
  }

  ngOnInit(): void {
    this.loadCategories();
    this.loadRelations();

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEdit = true;
      this.resourceId = id;
      this.loading.set(true);
      this.service.get(id).subscribe({
        next:  r  => { this.patchForm(r); this.loading.set(false); },
        error: () => { this.error.set('Impossible de charger la ressource.'); this.loading.set(false); },
      });
    }
  }

  toggleCategory(id: string): void {
    const cur = this.selectedCategories;
    this.form.patchValue({
      categories: cur.includes(id) ? cur.filter(c => c !== id) : [...cur, id],
    });
  }

  toggleRelation(id: string): void {
    const cur = this.selectedRelations;
    this.form.patchValue({
      relations: cur.includes(id) ? cur.filter(r => r !== id) : [...cur, id],
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    const payload = this.buildPayload();
    const req$ = this.isEdit
      ? this.service.update(this.resourceId, payload)
      : this.service.create(payload);
    req$.subscribe({
      next:  r  => this.router.navigate(['/resources', r.resource_id]),
      error: () => { this.error.set('Une erreur est survenue, veuillez réessayer.'); this.loading.set(false); },
    });
  }

  private patchForm(r: Resource): void {
    this.form.patchValue({
      resource_title:       r.resource_title,
      resource_description: r.resource_description ?? '',
      resource_label:       r.resource_label ?? '',
      categories:           r.categories.map(c => c.category_id),
      relations:            r.relations.map(rel => rel.relation_id),
      ...(r.reading_sheet  ?? {}),
      ...(r.games          ?? {}),
      ...(r.videos         ?? {}),
      ...(r.pdf            ?? {}),
      ...(r.activity       ?? {}),
      ...(r.article        ?? {}),
      ...(r.challenge_card ?? {}),
      ...(r.exercise       ?? {}),
    });
  }

  private buildPayload(): Partial<Resource> {
    const v     = this.form.value;
    const label = v.resource_label as ResourceLabel | '';

    const base: Record<string, unknown> = {
      resource_title:       v.resource_title,
      resource_description: v.resource_description || null,
      resource_label:       label || null,
      categories:           v.categories,
      relations:            v.relations,
    };

    if (label === 'reading_sheet') {
      base['detail'] = { book_title: v.book_title, book_author: v.book_author || null, summary: v.summary || null };
    } else if (label === 'games') {
      base['detail'] = { game_url: v.game_url || null, game_platform: v.game_platform || null, game_instructions: v.game_instructions || null };
    } else if (label === 'videos') {
      base['detail'] = { video_url: v.video_url, video_duration: v.video_duration, video_platform: v.video_platform || null };
    } else if (label === 'pdf') {
      base['detail'] = { pdf_url: v.pdf_url, pdf_publisher: v.pdf_publisher || null, pdf_page_count: v.pdf_page_count || null };
    } else if (label === 'activity') {
      base['detail'] = { activity_instructions: v.activity_instructions || null, activity_duration: v.activity_duration || null, activity_required_materials: v.activity_required_materials || null };
    } else if (label === 'article') {
      base['detail'] = { article_url: v.article_url, article_publisher: v.article_publisher || null };
    } else if (label === 'challenge_card') {
      base['detail'] = { challenge_card_duration: v.challenge_card_duration || null };
    } else if (label === 'exercise') {
      base['detail'] = { exercise_instructions: v.exercise_instructions || null, exercise_duration: v.exercise_duration || null };
    }

    return base as Partial<Resource>;
  }

  private loadCategories(): void {
    this.api.get<Category[]>('/api/resources/categories/').subscribe({
      next: res => this.categories.set(res),
      error: () => {},
    });
  }

  private loadRelations(): void {
    this.api.get<Relation[]>('/api/resources/relations/').subscribe({
      next: res => this.relations.set(res),
      error: () => {},
    });
  }
}
