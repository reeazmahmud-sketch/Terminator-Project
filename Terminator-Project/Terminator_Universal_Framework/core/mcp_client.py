# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Vertex AI Creative Studio MCP Client
Handles integration with Google's Model Context Protocol servers for media generation
"""

import httpx
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VertexAIMCPClient:
    """
    Client for interacting with Vertex AI Creative Studio MCP servers.
    Provides methods for image generation, video creation, speech synthesis,
    music generation, and audio/video compositing.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        timeout: float = 60.0
    ):
        """
        Initialize the MCP client.

        Args:
            project_id: Google Cloud project ID
            location: GCP region (default: us-central1)
            timeout: Request timeout in seconds
        """
        self.project_id = project_id
        self.location = location
        self.timeout = timeout

        # MCP Server endpoints
        self.servers = {
            'imagen': 'http://127.0.0.1:9000',
            'veo': 'http://127.0.0.1:9001',
            'chirp': 'http://127.0.0.1:9002',
            'lyria': 'http://127.0.0.1:9003',
            'avtool': 'http://127.0.0.1:9004'
        }

        # HTTP client
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"✅ MCP Client initialized for project: {project_id}")

    async def health_check(self) -> Dict[str, bool]:
        """Check health status of all MCP servers."""
        health = {}

        for server_name, endpoint in self.servers.items():
            try:
                response = await self.client.get(f"{endpoint}/health", timeout=5.0)
                health[server_name] = response.status_code == 200
                status = "✅" if health[server_name] else "❌"
                logger.info(f"{status} {server_name.upper()} server: {endpoint}")
            except Exception as e:
                health[server_name] = False
                logger.warning(f"❌ {server_name.upper()} server unreachable: {e}")

        return health

    # ============ IMAGEN METHODS (Image Generation & Editing) ============

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024x768",
        num_images: int = 1,
        guidance_scale: float = 7.5,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate images from text prompts using Imagen.

        Args:
            prompt: Text description of the image to generate
            negative_prompt: Text describing what NOT to include
            size: Output image size (e.g., "1024x768", "1024x1024")
            num_images: Number of images to generate (1-8)
            guidance_scale: How strictly to follow the prompt (1.0-20.0)
            style: Optional style preset (photorealistic, artistic, etc.)

        Returns:
            Dictionary with generated image URLs and metadata
        """
        try:
            if not prompt.strip():
                return {"error": "Prompt cannot be empty"}

            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "",
                "size": size,
                "num_images": min(num_images, 8),  # Cap at 8
                "guidance_scale": guidance_scale,
                "style": style
            }

            logger.info(f"🎨 Generating image: {prompt[:50]}...")
            response = await self.client.post(
                f"{self.servers['imagen']}/generate",
                json=payload
            )

            result = response.json()
            logger.info("✅ Image generation successful")
            return result

        except Exception as e:
            logger.error(f"❌ Image generation error: {e}")
            return {"error": str(e)}

    async def edit_image(
        self,
        image_url: str,
        prompt: str,
        mask_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit existing images with Imagen.

        Args:
            image_url: URL of the image to edit
            prompt: Description of desired edits
            mask_url: Optional mask URL for inpainting

        Returns:
            Dictionary with edited image URL and metadata
        """
        try:
            payload = {
                "image_url": image_url,
                "prompt": prompt,
                "mask_url": mask_url
            }

            logger.info(f"🎨 Editing image: {prompt[:50]}...")
            response = await self.client.post(
                f"{self.servers['imagen']}/edit",
                json=payload
            )

            result = response.json()
            logger.info("✅ Image editing successful")
            return result

        except Exception as e:
            logger.error(f"❌ Image editing error: {e}")
            return {"error": str(e)}

    # ============ VEO METHODS (Video Generation) ============

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        fps: int = 24,
        resolution: str = "720p",
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate videos from text prompts using Veo.

        Args:
            prompt: Text description of the video scene
            duration: Video duration in seconds (max 60)
            fps: Frames per second (24 or 30)
            resolution: Output resolution (480p, 720p, 1080p)
            style: Optional style preset

        Returns:
            Dictionary with generated video URL and metadata
        """
        try:
            if not prompt.strip():
                return {"error": "Prompt cannot be empty"}

            # Validate inputs
            duration = min(duration, 60)  # Cap at 60 seconds
            fps = 24 if fps < 30 else 30

            payload = {
                "prompt": prompt,
                "duration": duration,
                "fps": fps,
                "resolution": resolution,
                "style": style
            }

            logger.info(f"🎬 Generating video: {prompt[:50]}... ({duration}s)")
            response = await self.client.post(
                f"{self.servers['veo']}/generate",
                json=payload
            )

            result = response.json()
            logger.info("✅ Video generation successful")
            return result

        except Exception as e:
            logger.error(f"❌ Video generation error: {e}")
            return {"error": str(e)}

    async def generate_video_from_image(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5,
        fps: int = 24
    ) -> Dict[str, Any]:
        """
        Generate video from an existing image using Veo.

        Args:
            image_url: URL of the starting image
            prompt: Description of the animation
            duration: Duration in seconds
            fps: Frames per second

        Returns:
            Dictionary with generated video URL
        """
        try:
            payload = {
                "image_url": image_url,
                "prompt": prompt,
                "duration": duration,
                "fps": fps
            }

            logger.info(f"🎬 Generating video from image...")
            response = await self.client.post(
                f"{self.servers['veo']}/generate_from_image",
                json=payload
            )

            result = response.json()
            logger.info("✅ Video from image generation successful")
            return result

        except Exception as e:
            logger.error(f"❌ Video from image error: {e}")
            return {"error": str(e)}

    # ============ CHIRP METHODS (Audio/Speech Synthesis) ============

    async def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text using Chirp 3 HD.

        Args:
            text: Text to convert to speech
            language_code: Language code (e.g., 'en-US', 'en-GB', 'ja-JP')
            voice_name: Specific voice variant
            speaking_rate: Speed of speech (0.25-4.0)
            pitch: Pitch adjustment (-20.0 to 20.0)

        Returns:
            Dictionary with audio URL and metadata
        """
        try:
            if not text.strip():
                return {"error": "Text cannot be empty"}

            # Validate inputs
            speaking_rate = max(0.25, min(4.0, speaking_rate))
            pitch = max(-20.0, min(20.0, pitch))

            payload = {
                "text": text,
                "language_code": language_code,
                "voice_name": voice_name or f"{language_code}-Neural2-A",
                "speaking_rate": speaking_rate,
                "pitch": pitch
            }

            logger.info(f"🎤 Synthesizing speech ({language_code})...")
            response = await self.client.post(
                f"{self.servers['chirp']}/synthesize",
                json=payload
            )

            result = response.json()
            logger.info("✅ Speech synthesis successful")
            return result

        except Exception as e:
            logger.error(f"❌ Speech synthesis error: {e}")
            return {"error": str(e)}

    async def list_voices(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        List available voices for speech synthesis.

        Args:
            language_code: Filter by language (optional)

        Returns:
            Dictionary with available voices
        """
        try:
            params = {"language_code": language_code} if language_code else {}

            response = await self.client.get(
                f"{self.servers['chirp']}/voices",
                params=params
            )

            result = response.json()
            logger.info(f"✅ Retrieved voices list")
            return result

        except Exception as e:
            logger.error(f"❌ Error listing voices: {e}")
            return {"error": str(e)}

    # ============ LYRIA METHODS (Music Generation) ============

    async def generate_music(
        self,
        description: str,
        genre: str = "pop",
        mood: str = "neutral",
        duration: int = 60,
        tempo: Optional[int] = None,
        instruments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate music from text descriptions using Lyria.

        Args:
            description: Text description of desired music
            genre: Music genre (pop, rock, jazz, electronic, classical, ambient, etc.)
            mood: Mood/emotion (happy, sad, energetic, calm, mysterious, etc.)
            duration: Duration in seconds (max 300)
            tempo: BPM (optional, e.g., 120)
            instruments: List of desired instruments (optional)

        Returns:
            Dictionary with generated music URL and metadata
        """
        try:
            if not description.strip():
                return {"error": "Description cannot be empty"}

            # Validate duration
            duration = min(duration, 300)  # Cap at 5 minutes

            payload = {
                "description": description,
                "genre": genre,
                "mood": mood,
                "duration": duration,
                "tempo": tempo,
                "instruments": instruments or []
            }

            logger.info(f"🎵 Generating music ({genre}, {duration}s)...")
            response = await self.client.post(
                f"{self.servers['lyria']}/generate",
                json=payload
            )

            result = response.json()
            logger.info("✅ Music generation successful")
            return result

        except Exception as e:
            logger.error(f"❌ Music generation error: {e}")
            return {"error": str(e)}

    async def list_instruments(self) -> Dict[str, Any]:
        """
        List available instruments for music generation.

        Returns:
            Dictionary with available instruments
        """
        try:
            response = await self.client.get(f"{self.servers['lyria']}/instruments")
            result = response.json()
            logger.info("✅ Retrieved instruments list")
            return result

        except Exception as e:
            logger.error(f"❌ Error listing instruments: {e}")
            return {"error": str(e)}

    # ============ AVTOOL METHODS (Audio/Video Compositing) ============

    async def combine_audio_video(
        self,
        video_url: str,
        audio_url: str,
        output_format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Combine audio and video files using AVTool.

        Args:
            video_url: URL of the video file
            audio_url: URL of the audio file
            output_format: Output format (mp4, webm, mov, etc.)

        Returns:
            Dictionary with composed file URL
        """
        try:
            payload = {
                "operation": "combine_audio_video",
                "video_url": video_url,
                "audio_url": audio_url,
                "output_format": output_format
            }

            logger.info(f"🎬 Combining audio and video...")
            response = await self.client.post(
                f"{self.servers['avtool']}/process",
                json=payload
            )

            result = response.json()
            logger.info("✅ Audio/video combination successful")
            return result

        except Exception as e:
            logger.error(f"❌ Audio/video combination error: {e}")
            return {"error": str(e)}

    async def convert_format(
        self,
        input_url: str,
        output_format: str,
        file_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Convert media format using AVTool.

        Args:
            input_url: URL of the input file
            output_format: Desired output format
            file_type: Type of file (auto, video, audio)

        Returns:
            Dictionary with converted file URL
        """
        try:
            payload = {
                "operation": "convert_format",
                "input_url": input_url,
                "output_format": output_format,
                "file_type": file_type
            }

            logger.info(f"🔄 Converting format to {output_format}...")
            response = await self.client.post(
                f"{self.servers['avtool']}/process",
                json=payload
            )

            result = response.json()
            logger.info("✅ Format conversion successful")
            return result

        except Exception as e:
            logger.error(f"❌ Format conversion error: {e}")
            return {"error": str(e)}

    async def scale_video(
        self,
        video_url: str,
        resolution: str,
        maintain_aspect: bool = True
    ) -> Dict[str, Any]:
        """
        Scale video to different resolution using AVTool.

        Args:
            video_url: URL of the video file
            resolution: Target resolution (e.g., "1920x1080", "1280x720")
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            Dictionary with scaled video URL
        """
        try:
            payload = {
                "operation": "scale_video",
                "video_url": video_url,
                "resolution": resolution,
                "maintain_aspect": maintain_aspect
            }

            logger.info(f"📺 Scaling video to {resolution}...")
            response = await self.client.post(
                f"{self.servers['avtool']}/process",
                json=payload
            )

            result = response.json()
            logger.info("✅ Video scaling successful")
            return result

        except Exception as e:
            logger.error(f"❌ Video scaling error: {e}")
            return {"error": str(e)}

    async def concatenate_videos(
        self,
        video_urls: List[str],
        output_format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Concatenate multiple videos using AVTool.

        Args:
            video_urls: List of video URLs to concatenate
            output_format: Output format

        Returns:
            Dictionary with concatenated video URL
        """
        try:
            if not video_urls:
                return {"error": "At least one video URL is required"}

            payload = {
                "operation": "concatenate_videos",
                "video_urls": video_urls,
                "output_format": output_format
            }

            logger.info(f"🎞️  Concatenating {len(video_urls)} videos...")
            response = await self.client.post(
                f"{self.servers['avtool']}/process",
                json=payload
            )

            result = response.json()
            logger.info("✅ Video concatenation successful")
            return result

        except Exception as e:
            logger.error(f"❌ Video concatenation error: {e}")
            return {"error": str(e)}

    # ============ UTILITY METHODS ============

    async def batch_generate_images(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in parallel.

        Args:
            prompts: List of prompts to generate images for
            **kwargs: Additional arguments passed to generate_image

        Returns:
            List of generation results
        """
        logger.info(f"🎨 Batch generating {len(prompts)} images...")
        tasks = [
            self.generate_image(prompt, **kwargs)
            for prompt in prompts
        ]
        results = await asyncio.gather(*tasks)
        logger.info(f"✅ Batch generation complete")
        return results

    async def create_media_workflow(
        self,
        concept: str,
        include_image: bool = True,
        include_video: bool = True,
        include_music: bool = True
    ) -> Dict[str, Any]:
        """
        Create complete media workflow: image → video → music → composite.

        Args:
            concept: Main creative concept/description
            include_image: Generate initial image
            include_video: Generate video animation
            include_music: Generate background music

        Returns:
            Dictionary with all generated assets
        """
        logger.info(f"🎨 Creating media workflow for: {concept[:50]}...")

        workflow_result = {
            "concept": concept,
            "timestamp": datetime.now().isoformat(),
            "assets": {},
            "status": "completed"
        }

        try:
            # Step 1: Generate image
            if include_image:
                logger.info("Step 1: Generating base image...")
                image_result = await self.generate_image(
                    prompt=concept,
                    size="1024x768"
                )
                workflow_result["assets"]["image"] = image_result

            # Step 2: Generate video
            if include_video:
                logger.info("Step 2: Generating animated video...")
                video_prompt = f"Smooth animation of: {concept}"
                video_result = await self.generate_video(
                    prompt=video_prompt,
                    duration=5,
                    fps=24
                )
                workflow_result["assets"]["video"] = video_result

            # Step 3: Generate music
            if include_music:
                logger.info("Step 3: Generating background music...")
                music_result = await self.generate_music(
                    description=f"Background music for: {concept}",
                    duration=30
                )
                workflow_result["assets"]["music"] = music_result

            logger.info("✅ Media workflow complete")
            return workflow_result

        except Exception as e:
            logger.error(f"❌ Workflow error: {e}")
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            return workflow_result

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("✅ MCP Client closed")


# ============ STANDALONE USAGE EXAMPLE ============

async def demo():
    """Demonstration of MCP client usage."""

    # Initialize client
    client = VertexAIMCPClient(project_id="your-project-id")

    try:
        # Check server health
        print("\n🔍 Checking server health...")
        health = await client.health_check()

        # Generate image
        print("\n🎨 Generating image...")
        image = await client.generate_image(
            prompt="A serene mountain landscape at sunset"
        )
        print(f"Image result: {image}")

        # Synthesize speech
        print("\n🎤 Synthesizing speech...")
        speech = await client.synthesize_speech(
            text="Welcome to Terminator, your AI creative assistant"
        )
        print(f"Speech result: {speech}")

        # Generate music
        print("\n🎵 Generating music...")
        music = await client.generate_music(
            description="Relaxing ambient music for meditation",
            duration=120
        )
        print(f"Music result: {music}")

    finally:
        await client.close()


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())
