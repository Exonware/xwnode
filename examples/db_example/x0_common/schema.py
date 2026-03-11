"""
Entity Schemas and Data Generators - Full Social Media Platform
Defines comprehensive data model for benchmarking: Users, Posts, Comments, Relationships,
Likes, Shares, Messages, Notifications, Groups, Events, and more.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.2
Generation Date: December 2, 2025
"""

import uuid
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Optional
@dataclass

class User:
    """Full social media user profile with comprehensive fields"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    display_name: str = ""
    bio: str = ""
    profile_picture_url: str = ""
    cover_photo_url: str = ""
    location: str = ""
    website: str = ""
    birth_date: Optional[str] = None
    phone_number: str = ""
    is_verified: bool = False
    is_private: bool = False
    is_active: bool = True
    language: str = "en"
    timezone: str = "UTC"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login_at: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    like_count: int = 0
    # Privacy settings
    privacy_show_email: bool = False
    privacy_show_phone: bool = False
    privacy_show_birthday: bool = False
    # Preferences
    notification_email: bool = True
    notification_push: bool = True
    notification_sms: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'User':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Post:
    """Full social media post with media, hashtags, mentions, and engagement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    content: str = ""
    title: Optional[str] = None  # Optional title for some post types
    post_type: str = "text"  # text, image, video, link, poll, event
    # Media attachments
    media_urls: list[str] = field(default_factory=list)  # Images, videos
    media_types: list[str] = field(default_factory=list)  # image/jpeg, video/mp4, etc.
    # Engagement
    hashtags: list[str] = field(default_factory=list)  # #hashtag1, #hashtag2
    mentions: list[str] = field(default_factory=list)  # @username1, @username2
    tagged_users: list[str] = field(default_factory=list)  # User IDs tagged in post
    # Location
    location_name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    # Visibility and settings
    visibility: str = "public"  # public, friends, private, unlisted
    allow_comments: bool = True
    allow_shares: bool = True
    is_pinned: bool = False
    is_edited: bool = False
    edited_at: Optional[str] = None
    # Engagement metrics
    likes_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    view_count: int = 0
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_at: Optional[str] = None
    # Additional metadata
    link_preview_url: Optional[str] = None
    link_preview_title: Optional[str] = None
    link_preview_description: Optional[str] = None
    link_preview_image: Optional[str] = None
    poll_question: Optional[str] = None
    poll_options: list[str] = field(default_factory=list)
    poll_votes: dict[str, int] = field(default_factory=dict)
    poll_ends_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Post':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Comment:
    """Full social media comment with replies, reactions, and mentions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str = ""
    user_id: str = ""
    parent_comment_id: Optional[str] = None  # For nested replies
    content: str = ""
    # Media in comments
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    # Mentions
    mentions: list[str] = field(default_factory=list)  # @username mentions
    # Engagement
    likes_count: int = 0
    reply_count: int = 0
    # Status
    is_deleted: bool = False
    is_edited: bool = False
    edited_at: Optional[str] = None
    is_pinned: bool = False  # Pinned by post author
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Comment':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Relationship:
    """Comprehensive user relationship with multiple types and metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_user_id: str = ""
    target_user_id: str = ""
    relationship_type: str = "follows"  # follows, friend, block, mute, subscribe
    status: str = "active"  # active, pending, blocked, muted
    is_mutual: bool = False  # For friend relationships
    # Notification settings
    notify_on_posts: bool = True
    notify_on_stories: bool = True
    notify_on_live: bool = True
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None  # For temporary mutes/blocks

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Relationship':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Like:
    """Like/reaction entity for posts and comments"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    target_type: str = "post"  # post, comment, message
    target_id: str = ""
    reaction_type: str = "like"  # like, love, laugh, wow, sad, angry
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Like':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Share:
    """Share/repost entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    post_id: str = ""
    share_type: str = "repost"  # repost, quote, story, message
    quote_text: Optional[str] = None  # For quote shares
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Share':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Message:
    """Direct message between users"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    sender_id: str = ""
    recipient_id: str = ""
    content: str = ""
    message_type: str = "text"  # text, image, video, file, voice, location
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    is_read: bool = False
    read_at: Optional[str] = None
    is_deleted: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Notification:
    """User notification for various events"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    notification_type: str = "like"  # like, comment, follow, mention, message, etc.
    actor_id: str = ""  # User who triggered the notification
    target_type: str = "post"  # post, comment, user, message
    target_id: str = ""
    title: str = ""
    body: str = ""
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    is_read: bool = False
    read_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Notification':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Group:
    """User group/community"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    owner_id: str = ""
    cover_image_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    group_type: str = "public"  # public, private, secret
    member_count: int = 0
    post_count: int = 0
    category: str = ""  # technology, sports, music, etc.
    rules: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Group':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Event:
    """Social event"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    organizer_id: str = ""
    location_name: str = ""
    location_address: str = ""
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    start_time: str = ""
    end_time: Optional[str] = None
    timezone: str = "UTC"
    is_online: bool = False
    online_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    attendee_count: int = 0
    maybe_count: int = 0
    not_going_count: int = 0
    event_type: str = "public"  # public, private, invite_only
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Event':
        """Create from dictionary"""
        return cls(**data)
@dataclass

class Hashtag:
    """Hashtag tracking and trending"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # Without # symbol
    post_count: int = 0
    trend_score: float = 0.0
    is_trending: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> 'Hashtag':
        """Create from dictionary"""
        return cls(**data)
# ============================================================================
# DATA GENERATORS - Full Social Media Platform
# ============================================================================
# Sample data for realistic generation
FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Sage", "River",
               "Blake", "Cameron", "Dakota", "Emery", "Finley", "Hayden", "Jamie", "Kendall", "Logan", "Parker"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
          "Dallas", "San Jose", "Austin", "Jacksonville", "San Francisco", "Columbus", "Fort Worth", "Charlotte",
          "Seattle", "Denver", "Boston", "Nashville"]
HASHTAGS = ["technology", "coding", "programming", "ai", "machinelearning", "webdev", "python", "javascript",
            "react", "nodejs", "cloud", "devops", "startup", "business", "marketing", "design", "photography",
            "travel", "food", "fitness", "music", "art", "science", "news", "politics"]
REACTION_TYPES = ["like", "love", "laugh", "wow", "sad", "angry"]
POST_TYPES = ["text", "image", "video", "link", "poll"]
VISIBILITY_TYPES = ["public", "friends", "private", "unlisted"]
RELATIONSHIP_TYPES = ["follows", "friend", "block", "mute", "subscribe"]


def generate_user(index: int) -> User:
    """Generate a comprehensive social media user profile"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name.lower()}{last_name.lower()}{index}"
    display_name = f"{first_name} {last_name}"
    # Generate realistic dates
    base_date = datetime.now() - timedelta(days=random.randint(30, 3650))  # 30 days to 10 years ago
    created_at = base_date.isoformat()
    last_login = (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
    birth_date = (datetime.now() - timedelta(days=random.randint(18*365, 65*365))).isoformat()
    return User(
        username=username,
        email=f"{username}@example.com",
        display_name=display_name,
        bio=f"Passionate about technology, innovation, and connecting with amazing people! 🚀 #TechEnthusiast",
        profile_picture_url=f"https://example.com/profiles/{username}.jpg",
        cover_photo_url=f"https://example.com/covers/{username}.jpg",
        location=random.choice(CITIES),
        website=f"https://{username}.com",
        birth_date=birth_date,
        phone_number=f"+1{random.randint(2000000000, 9999999999)}",
        is_verified=random.random() < 0.05,  # 5% verified
        is_private=random.random() < 0.15,  # 15% private
        is_active=True,
        language=random.choice(["en", "es", "fr", "de", "zh", "ja"]),
        timezone=random.choice(["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]),
        created_at=created_at,
        last_login_at=last_login,
        follower_count=random.randint(0, 10000),
        following_count=random.randint(0, 2000),
        post_count=random.randint(0, 500),
        like_count=random.randint(0, 5000),
        privacy_show_email=random.random() < 0.2,
        privacy_show_phone=random.random() < 0.1,
        privacy_show_birthday=random.random() < 0.3,
        notification_email=True,
        notification_push=random.random() < 0.8,
        notification_sms=random.random() < 0.3
    )


def generate_post(index: int, user_id: str, user_ids: Optional[list[str]] = None) -> Post:
    """
    Generate a comprehensive social media post.
    Root cause fixed: Made user_ids optional for backward compatibility with existing benchmarks.
    Solution: Default to empty list if not provided, allowing old code to work while new code
    can pass user_ids for enhanced features like mentions and tagged users.
    Priority #3: Maintainability - Preserve backward compatibility.
    Args:
        index: Post index
        user_id: ID of user creating the post
        user_ids: Optional list of all user IDs (for mentions/tagging). Defaults to empty list.
    """
    if user_ids is None:
        user_ids = []
    post_type = random.choice(POST_TYPES)
    content = f"This is post #{index}. "
    # Add realistic content based on type
    if post_type == "text":
        content += "Sharing some thoughts on the latest developments in technology and innovation. "
        content += "What do you think about this? Let's discuss! 💭"
    elif post_type == "image":
        content += "Check out this amazing photo I took! 📸"
    elif post_type == "video":
        content += "Just uploaded a new video! Watch and let me know what you think! 🎥"
    elif post_type == "link":
        content += "Found this interesting article: https://example.com/article/{index}"
    elif post_type == "poll":
        content += "Quick poll: What's your favorite programming language?"
    # Generate hashtags (2-5 per post)
    num_hashtags = random.randint(2, 5)
    hashtags = [f"#{random.choice(HASHTAGS)}" for _ in range(num_hashtags)]
    # Generate mentions (0-3 per post) - only if user_ids provided
    num_mentions = random.randint(0, 3) if user_ids else 0
    mentions = [f"@{random.choice(user_ids)}" for _ in range(num_mentions) if user_ids]
    # Generate media if applicable
    media_urls = []
    media_types = []
    if post_type in ["image", "video"]:
        num_media = random.randint(1, 4) if post_type == "image" else 1
        for i in range(num_media):
            media_urls.append(f"https://example.com/media/post_{index}_media_{i}.{'jpg' if post_type == 'image' else 'mp4'}")
            media_types.append(f"{'image' if post_type == 'image' else 'video'}/{'jpeg' if post_type == 'image' else 'mp4'}")
    # Generate poll if applicable
    poll_question = None
    poll_options = []
    poll_votes = {}
    poll_ends_at = None
    if post_type == "poll":
        poll_question = "What's your favorite programming language?"
        poll_options = ["Python", "JavaScript", "Java", "Go", "Rust"]
        poll_votes = {opt: random.randint(0, 100) for opt in poll_options}
        poll_ends_at = (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat()
    # Generate location (30% of posts)
    location_name = None
    location_lat = None
    location_lng = None
    if random.random() < 0.3:
        location_name = random.choice(CITIES)
        location_lat = round(random.uniform(-90, 90), 6)
        location_lng = round(random.uniform(-180, 180), 6)
    created_at = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
    return Post(
        user_id=user_id,
        content=content,
        post_type=post_type,
        media_urls=media_urls,
        media_types=media_types,
        hashtags=hashtags,
        mentions=mentions,
        tagged_users=random.sample(user_ids, min(random.randint(0, 3), len(user_ids))) if user_ids else [],
        location_name=location_name,
        location_lat=location_lat,
        location_lng=location_lng,
        visibility=random.choice(VISIBILITY_TYPES),
        allow_comments=True,
        allow_shares=True,
        is_pinned=random.random() < 0.05,  # 5% pinned
        is_edited=random.random() < 0.1,  # 10% edited
        edited_at=(datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat() if random.random() < 0.1 else None,
        likes_count=random.randint(0, 1000),
        comment_count=random.randint(0, 100),
        share_count=random.randint(0, 50),
        view_count=random.randint(0, 10000),
        created_at=created_at,
        link_preview_url=f"https://example.com/article/{index}" if post_type == "link" else None,
        link_preview_title=f"Article Title {index}" if post_type == "link" else None,
        link_preview_description=f"Article description for post {index}" if post_type == "link" else None,
        link_preview_image=f"https://example.com/previews/{index}.jpg" if post_type == "link" else None,
        poll_question=poll_question,
        poll_options=poll_options,
        poll_votes=poll_votes,
        poll_ends_at=poll_ends_at
    )


def generate_comment(index: int, post_id: str, user_id: str, user_ids: Optional[list[str]] = None, parent_comment_id: Optional[str] = None) -> Comment:
    """
    Generate a comprehensive social media comment.
    Root cause fixed: Made user_ids optional for backward compatibility with existing benchmarks.
    Solution: Default to empty list if not provided, allowing old code to work while new code
    can pass user_ids for enhanced features like mentions.
    Priority #3: Maintainability - Preserve backward compatibility.
    Args:
        index: Comment index
        post_id: ID of post being commented on
        user_id: ID of user making the comment
        user_ids: Optional list of all user IDs (for mentions). Defaults to empty list.
        parent_comment_id: Optional ID of parent comment (for nested replies)
    """
    if user_ids is None:
        user_ids = []
    content = f"Great post! This is comment #{index}. "
    content += random.choice([
        "I totally agree!",
        "Interesting perspective!",
        "Thanks for sharing!",
        "This is really helpful!",
        "Looking forward to more!",
    ])
    # 20% chance of mentions - only if user_ids provided
    mentions = []
    if random.random() < 0.2 and user_ids:
        num_mentions = random.randint(1, 2)
        mentions = [f"@{random.choice(user_ids)}" for _ in range(num_mentions)]
    # 10% chance of media in comment
    media_url = None
    media_type = None
    if random.random() < 0.1:
        media_url = f"https://example.com/comments/{index}.jpg"
        media_type = "image/jpeg"
    created_at = (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
    return Comment(
        post_id=post_id,
        user_id=user_id,
        parent_comment_id=parent_comment_id,
        content=content,
        media_url=media_url,
        media_type=media_type,
        mentions=mentions,
        likes_count=random.randint(0, 50),
        reply_count=random.randint(0, 10) if parent_comment_id is None else 0,
        is_deleted=random.random() < 0.02,  # 2% deleted
        is_edited=random.random() < 0.05,  # 5% edited
        edited_at=(datetime.now() - timedelta(hours=random.randint(1, 6))).isoformat() if random.random() < 0.05 else None,
        is_pinned=random.random() < 0.01,  # 1% pinned
        created_at=created_at
    )


def generate_relationship(source_id: str, target_id: str, rel_type: Optional[str] = None) -> Relationship:
    """Generate a comprehensive user relationship"""
    if rel_type is None:
        rel_type = random.choice(RELATIONSHIP_TYPES)
    created_at = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
    return Relationship(
        source_user_id=source_id,
        target_user_id=target_id,
        relationship_type=rel_type,
        status="active" if rel_type != "block" else random.choice(["active", "blocked"]),
        is_mutual=rel_type == "friend" and random.random() < 0.7,  # 70% mutual for friends
        notify_on_posts=rel_type in ["follows", "friend"] and random.random() < 0.8,
        notify_on_stories=rel_type in ["follows", "friend"] and random.random() < 0.6,
        notify_on_live=rel_type in ["follows", "friend"] and random.random() < 0.4,
        created_at=created_at,
        updated_at=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat() if random.random() < 0.3 else None,
        expires_at=(datetime.now() + timedelta(days=random.randint(1, 30))).isoformat() if rel_type == "mute" and random.random() < 0.5 else None
    )


def generate_like(user_id: str, target_type: str, target_id: str) -> Like:
    """Generate a like/reaction"""
    return Like(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        reaction_type=random.choice(REACTION_TYPES),
        created_at=(datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
    )


def generate_share(user_id: str, post_id: str) -> Share:
    """Generate a share/repost"""
    share_type = random.choice(["repost", "quote", "story"])
    quote_text = f"Amazing content! 🔥" if share_type == "quote" else None
    return Share(
        user_id=user_id,
        post_id=post_id,
        share_type=share_type,
        quote_text=quote_text,
        created_at=(datetime.now() - timedelta(days=random.randint(0, 3))).isoformat()
    )


def generate_message(conversation_id: str, sender_id: str, recipient_id: str) -> Message:
    """Generate a direct message"""
    message_type = random.choice(["text", "image", "video", "file"])
    content = f"Hey! This is message content. How are you doing?"
    media_url = None
    media_type = None
    if message_type != "text":
        media_url = f"https://example.com/messages/{uuid.uuid4()}.{'jpg' if message_type == 'image' else 'mp4' if message_type == 'video' else 'pdf'}"
        media_type = f"{message_type}/{('jpeg' if message_type == 'image' else 'mp4' if message_type == 'video' else 'pdf')}"
    return Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content,
        message_type=message_type,
        media_url=media_url,
        media_type=media_type,
        is_read=random.random() < 0.7,  # 70% read
        read_at=(datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat() if random.random() < 0.7 else None,
        is_deleted=random.random() < 0.05,  # 5% deleted
        created_at=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
    )


def generate_notification(user_id: str, actor_id: str, notification_type: str, target_type: str, target_id: str) -> Notification:
    """Generate a user notification"""
    titles = {
        "like": f"New like on your {target_type}",
        "comment": "New comment on your post",
        "follow": "New follower",
        "mention": "You were mentioned",
        "message": "New message",
        "share": "Your post was shared"
    }
    bodies = {
        "like": f"Someone liked your {target_type}",
        "comment": "Someone commented on your post",
        "follow": "Someone started following you",
        "mention": "Someone mentioned you in a post",
        "message": "You have a new message",
        "share": "Someone shared your post"
    }
    return Notification(
        user_id=user_id,
        notification_type=notification_type,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        title=titles.get(notification_type, "New notification"),
        body=bodies.get(notification_type, "You have a new notification"),
        image_url=f"https://example.com/notifications/{notification_type}.jpg",
        link_url=f"https://example.com/{target_type}s/{target_id}",
        is_read=random.random() < 0.6,  # 60% read
        read_at=(datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat() if random.random() < 0.6 else None,
        created_at=(datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
    )


def generate_group(index: int, owner_id: str) -> Group:
    """Generate a user group/community"""
    group_name = f"{random.choice(['Tech', 'Sports', 'Music', 'Art', 'Science', 'Business'])} Community {index}"
    return Group(
        name=group_name,
        description=f"Welcome to {group_name}! A place for enthusiasts to connect and share.",
        owner_id=owner_id,
        cover_image_url=f"https://example.com/groups/{index}/cover.jpg",
        profile_image_url=f"https://example.com/groups/{index}/profile.jpg",
        group_type=random.choice(["public", "private", "secret"]),
        member_count=random.randint(10, 10000),
        post_count=random.randint(0, 1000),
        category=random.choice(["technology", "sports", "music", "art", "science", "business", "education"]),
        rules=[
            "Be respectful to all members",
            "No spam or self-promotion",
            "Keep discussions relevant to the group topic"
        ],
        tags=[random.choice(HASHTAGS) for _ in range(random.randint(2, 5))],
        created_at=(datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
        is_active=True
    )


def generate_event(index: int, organizer_id: str) -> Event:
    """Generate a social event"""
    event_name = f"{random.choice(['Tech', 'Music', 'Business', 'Art'])} Meetup {index}"
    start_time = datetime.now() + timedelta(days=random.randint(1, 90))
    end_time = start_time + timedelta(hours=random.randint(2, 8))
    return Event(
        name=event_name,
        description=f"Join us for {event_name}! An exciting event you won't want to miss.",
        organizer_id=organizer_id,
        location_name=random.choice(CITIES),
        location_address=f"{random.randint(100, 9999)} Main Street, {random.choice(CITIES)}",
        location_lat=round(random.uniform(-90, 90), 6),
        location_lng=round(random.uniform(-180, 180), 6),
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        timezone=random.choice(["UTC", "America/New_York", "America/Los_Angeles", "Europe/London"]),
        is_online=random.random() < 0.2,  # 20% online
        online_url=f"https://example.com/events/{index}/live" if random.random() < 0.2 else None,
        cover_image_url=f"https://example.com/events/{index}/cover.jpg",
        attendee_count=random.randint(0, 500),
        maybe_count=random.randint(0, 100),
        not_going_count=random.randint(0, 50),
        event_type=random.choice(["public", "private", "invite_only"]),
        created_at=(datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
    )


def generate_hashtag(name: str) -> Hashtag:
    """Generate a hashtag"""
    return Hashtag(
        name=name,
        post_count=random.randint(0, 10000),
        trend_score=round(random.uniform(0, 100), 2),
        is_trending=random.random() < 0.1,  # 10% trending
        created_at=(datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
        last_used_at=(datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
    )
