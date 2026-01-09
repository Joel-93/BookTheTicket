from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = 'Add sample trailer URLs to movies'

    def handle(self, *args, **options):
        # Sample YouTube trailer URLs - using known embeddable videos
        sample_trailers = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Rick Roll (known to be embeddable)
            'https://www.youtube.com/watch?v=jNQXAC9IVRw',  # Another video
            'https://www.youtube.com/watch?v=kJQP7kiw5Fk',  # Sample
            'https://www.youtube.com/watch?v=oHg5SJYRHA0',  # Another
        ]
        
        movies = Movie.objects.all()
        count = 0
        for i, movie in enumerate(movies):
            movie.trailer_url = sample_trailers[i % len(sample_trailers)]
            movie.save()
            count += 1
            self.stdout.write(f'Updated trailer for {movie.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated trailers for {count} movies')
        )