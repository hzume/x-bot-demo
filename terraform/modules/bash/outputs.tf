output "image_digest_follow" {
  value = data.local_file.image_digest_follow.content
}

output "image_digest_post" {
  value = data.local_file.image_digest_post.content
}
