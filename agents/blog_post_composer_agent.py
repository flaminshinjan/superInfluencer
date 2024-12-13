class BlogPostComposerAgent:
    def run(self, validated_content):
        if validated_content["status"] == "good":
            blog_post = {
                "title": "Empowering Innovation",
                "content": validated_content["content"],
                "tags": ["innovation", "vision", "mission"]
            }
            return {"blog_post": blog_post}
        else:
            return {"error": "Content not suitable for a blog post."}
