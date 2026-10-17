"""Tool declaration/handler wiring; execution stays owned by ToolExecutor."""
import os


def register_executor_tools(executor):
    """Populate the ToolRegistry with all tools, grouped by toolset.

    Each toolset gets:
      - Its schema declarations (from tool_declarations.py)
      - Its handlers (bound methods from this class)
      - An optional check_fn for runtime availability
      - An optional requires_env list
    """
    from tools.tool_registry import registry
    from tools.tool_declarations import (
        CORE_TOOLS, TOOLSET_MANAGEMENT_TOOLS,
        PERCEPTION_TOOLS, WEB_TOOLS, FILES_TOOLS,
        BROWSER_TOOLS, GIT_TOOLS, GITHUB_TOOLS,
        MOLTBOOK_TOOLS, EMAIL_TOOLS, CALENDAR_TOOLS,
        DRIVE_TOOLS, TASKS_TOOLS, DESKTOP_TOOLS,
    )
    executor._registry = registry

    # Presentation-only extension: expose the dashboard canvas as an
    # optional toolset without altering the pulse or memory architecture.
    from tools.ui_canvas_tool import register_ui_canvas_tool
    register_ui_canvas_tool(registry)

    # ── Availability check functions ─────────────────────────────
    def _check_github():
        return bool(os.environ.get("GITHUB_TOKEN"))

    def _check_google_creds():
        # Google token is at ~/.config/helix/google_token.json
        # (loaded by main.py's _load_credentials)
        creds_path = os.path.expanduser("~/.config/helix/google_token.json")
        return os.path.exists(creds_path)

    def _check_moltbook():
        # Moltbook API key is set in credentials.env
        return bool(os.environ.get("MOLTBOOK_API_KEY"))

    def _check_desktop():
        # xdotool required for desktop control
        try:
            import subprocess
            subprocess.run(["which", "xdotool"], capture_output=True, check=True)
            return True
        except Exception:
            return False

    def _check_camera_enabled():
        try:
            from core.pulse_loop import PulseLoop
            cfg = PulseLoop._load_config()
            if not cfg.get("camera_enabled", True):
                return False
        except Exception:
            pass
        import glob
        return len(glob.glob("/dev/video*")) > 0

    def _check_ptz_enabled():
        if not _check_camera_enabled():
            return False
        try:
            from core.pulse_loop import PulseLoop
            cfg = PulseLoop._load_config()
            return bool(cfg.get("ptz_enabled", False))
        except Exception:
            return False

    def _check_mic_enabled():
        try:
            from core.pulse_loop import PulseLoop
            cfg = PulseLoop._load_config()
            return bool(cfg.get("mic_enabled", True))
        except Exception:
            return True

    # ── Build handler maps (bound methods) ───────────────────────
    core_handlers = {
        "reply": executor._fc_reply,
        "send_message": executor._fc_send_message,
        "terminal": executor._fc_terminal,
        "verbalize": executor._fc_verbalize,
        "memory_recall": executor._fc_memory_recall,
        "note": executor._fc_note,
        "note_write": executor._fc_note,
        "note_append": executor._fc_update_note,
        "note_clear": executor._fc_clear_notes,
        "note_done": executor._fc_note_done,
        "list_notes": executor._fc_list_notes,
        "clear_notes": executor._fc_clear_notes,
        "update_note": executor._fc_update_note,
        "journal": executor._fc_journal,
        "nap": executor._fc_reset_context,
        "reset_context": executor._fc_reset_context,
    }
    perception_handlers = {
        "listen": executor._fc_listen,
        "look": executor._fc_look,
        "ptz_look": executor._fc_ptz_look,
        "camera_auto_track": executor._fc_camera_auto_track,
        "record_video": executor._fc_record_video,
    }
    web_handlers = {
        "search": executor._fc_search,
        "read_url": executor._fc_read_url,
    }
    files_handlers = {
        "read_file": executor._fc_read_file,
        "write_file": executor._fc_write_file,
        "append_file": executor._fc_append_file,
    }
    mgmt_handlers = {
        "enable_toolset": executor._fc_enable_toolset,
        "disable_toolset": executor._fc_disable_toolset,
        "list_toolsets": executor._fc_list_toolsets,
    }
    browser_handlers = {
        "browse": executor._fc_browse,
        "browse_interact": executor._fc_browse_interact,
        "browse_observe": executor._fc_browse_observe,
        "browse_screenshot": executor._fc_browse_screenshot,
    }
    git_handlers = {
        "git_status": executor._fc_git_status,
        "git_diff": executor._fc_git_diff,
        "git_commit": executor._fc_git_commit,
        "git_push": executor._fc_git_push,
        "git_pull": executor._fc_git_pull,
        "git_log": executor._fc_git_log,
        "git_clone": executor._fc_git_clone,
    }
    github_handlers = {
        "github_search": executor._fc_github_search,
        "github_issue": executor._fc_github_issue,
        "github_create_issue": executor._fc_github_create_issue,
        "github_comment": executor._fc_github_comment,
        "github_pr": executor._fc_github_pr,
    }
    moltbook_handlers = {
        "moltbook_home": executor._fc_moltbook_home,
        "moltbook_feed": executor._fc_moltbook_feed,
        "moltbook_read": executor._fc_moltbook_read,
        "moltbook_post": executor._fc_moltbook_post,
        "moltbook_comment": executor._fc_moltbook_comment,
        "moltbook_vote": executor._fc_moltbook_vote,
        "moltbook_search": executor._fc_moltbook_search,
        "moltbook_profile": executor._fc_moltbook_profile,
        "moltbook_user_posts": executor._fc_moltbook_user_posts,
        "moltbook_follow": executor._fc_moltbook_follow,
        "moltbook_unfollow": executor._fc_moltbook_unfollow,
        "moltbook_submolts": executor._fc_moltbook_submolts,
        "moltbook_delete": executor._fc_moltbook_delete,
        "moltbook_notifications": executor._fc_moltbook_notifications,
        "moltbook_notifications_read": executor._fc_moltbook_notifications_read,
    }
    email_handlers = {
        "email_send": executor._fc_email_send,
        "email_read": executor._fc_email_read,
        "email_search": executor._fc_email_search,
        "email_get": executor._fc_email_get,
        "email_reply": executor._fc_email_reply,
        "email_forward": executor._fc_email_forward,
        "email_mark_read": executor._fc_email_mark_read,
    }
    calendar_handlers = {
        "calendar_create": executor._fc_calendar_create,
        "calendar_list": executor._fc_calendar_list,
        "calendar_delete": executor._fc_calendar_delete,
    }
    drive_handlers = {
        "drive_search": executor._fc_drive_search,
        "drive_read": executor._fc_drive_read,
        "drive_list": executor._fc_drive_list,
        "drive_upload": executor._fc_drive_upload,
        "drive_share": executor._fc_drive_share,
    }
    tasks_handlers = {
        "tasks_lists": executor._fc_tasks_lists,
        "tasks_list": executor._fc_tasks_list,
        "tasks_create": executor._fc_tasks_create,
        "tasks_complete": executor._fc_tasks_complete,
        "tasks_delete": executor._fc_tasks_delete,
    }
    desktop_handlers = {
        "desktop_type": executor._fc_desktop_type,
        "desktop_key": executor._fc_desktop_key,
        "desktop_click": executor._fc_desktop_click,
        "desktop_mouse": executor._fc_desktop_mouse,
        "desktop_scroll": executor._fc_desktop_scroll,
        "desktop_window": executor._fc_desktop_window,
        "desktop_focus": executor._fc_desktop_focus,
        "desktop_open": executor._fc_desktop_open,
        "desktop_open_url": executor._fc_desktop_open_url,
        "desktop_screenshot": executor._fc_desktop_screenshot,
    }

    # ── Register all toolsets ─────────────────────────────────────
    registry.register_batch(
        toolset="core",
        tools=CORE_TOOLS + TOOLSET_MANAGEMENT_TOOLS,
        handlers={**core_handlers, **mgmt_handlers},
        description="Core cognitive tools — always loaded",
        focus_types={
            "terminal": "focus",
        },
    )
    registry.register_toolset_description("perception", "Physical senses — camera and microphone")
    for tool in PERCEPTION_TOOLS:
        name = tool["name"]
        handler = perception_handlers.get(name)
        if handler:
            chk = None
            if name in ("look", "record_video"):
                chk = _check_camera_enabled
            elif name in ("ptz_look", "camera_auto_track"):
                chk = _check_ptz_enabled
            elif name == "listen":
                chk = _check_mic_enabled
            registry.register(
                name=name,
                toolset="perception",
                schema=tool,
                handler=handler,
                check_fn=chk,
                focus_type="focus",
            )
    registry.register_batch(
        toolset="web",
        tools=WEB_TOOLS,
        handlers=web_handlers,
        description="Web search and page content reading",
        focus_types={
            "search": "focus",
            "read_url": "focus",
        },
    )
    registry.register_batch(
        toolset="files",
        tools=FILES_TOOLS,
        handlers=files_handlers,
        description="Local filesystem operations (read, write, append)",
        focus_types={
            "write_file": "focus",
            "append_file": "focus",
            "read_file": "intake",
        },
    )
    registry.register_batch(
        toolset="browser",
        tools=BROWSER_TOOLS,
        handlers=browser_handlers,
        description="Web browsing and page interaction",
        focus_types={
            "browse": "focus",
            "browse_interact": "focus",
            "browse_observe": "intake",
        },
    )
    registry.register_batch(
        toolset="git",
        tools=GIT_TOOLS,
        handlers=git_handlers,
        description="Local Git repository operations",
        focus_types={
            "git_commit": "focus",
            "git_push": "focus",
            "git_diff": "focus",
        },
    )
    registry.register_batch(
        toolset="github",
        tools=GITHUB_TOOLS,
        handlers=github_handlers,
        check_fn=_check_github,
        requires_env=["GITHUB_TOKEN"],
        description="GitHub API — search repos, manage issues, PRs",
        focus_types={
            "github_search": "focus",
            "github_create_issue": "focus",
        },
    )
    registry.register_batch(
        toolset="social",
        tools=MOLTBOOK_TOOLS,
        handlers=moltbook_handlers,
        check_fn=_check_moltbook,
        description="Moltbook social platform",
        focus_types={
            "moltbook_post": "focus",
            "moltbook_read": "intake",
            "moltbook_feed": "intake",
            "moltbook_home": "intake",
            "moltbook_notifications": "intake",
        },
    )
    registry.register_batch(
        toolset="email",
        tools=EMAIL_TOOLS,
        handlers=email_handlers,
        check_fn=_check_google_creds,
        requires_env=["GOOGLE_CREDENTIALS"],
        description="Gmail — send, read, search, reply, forward",
        focus_types={
            "email_read": "intake",
            "email_get": "intake",
            "email_search": "intake",
        },
    )
    registry.register_batch(
        toolset="calendar",
        tools=CALENDAR_TOOLS,
        handlers=calendar_handlers,
        check_fn=_check_google_creds,
        requires_env=["GOOGLE_CREDENTIALS"],
        description="Google Calendar — create, list, delete events",
        focus_types={
            "calendar_list": "intake",
        },
    )
    registry.register_batch(
        toolset="drive",
        tools=DRIVE_TOOLS,
        handlers=drive_handlers,
        check_fn=_check_google_creds,
        requires_env=["GOOGLE_CREDENTIALS"],
        description="Google Drive — search, read, list, upload, share",
        focus_types={
            "drive_read": "intake",
            "drive_search": "intake",
            "drive_list": "intake",
        },
    )
    registry.register_batch(
        toolset="tasks",
        tools=TASKS_TOOLS,
        handlers=tasks_handlers,
        check_fn=_check_google_creds,
        requires_env=["GOOGLE_CREDENTIALS"],
        description="Google Tasks — task lists, create, complete",
    )
    registry.register_batch(
        toolset="desktop",
        tools=DESKTOP_TOOLS,
        handlers=desktop_handlers,
        check_fn=_check_desktop,
        description="Desktop control — typing, clicking, screenshots",
        focus_types={
            "desktop_type": "focus",
            "desktop_click": "focus",
            "desktop_key": "focus",
            "desktop_open_url": "focus",
        },
    )
