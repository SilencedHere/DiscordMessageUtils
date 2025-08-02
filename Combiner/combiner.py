import json
from datetime import datetime
from typing import List, Dict, Any


def parse_message_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parse a Discord message file and return a list of message dictionaries.
    Handles both JSON and malformed JSON-like formats.
    """
    messages = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Try to parse as standard JSON first
        try:
            if content.startswith('[') and content.endswith(']'):
                messages = json.loads(content)
            else:
                # Handle malformed JSON-like format
                # Add brackets if missing and fix trailing commas
                if not content.startswith('['):
                    content = '[' + content
                if not content.endswith(']'):
                    content = content.rstrip(',') + ']'

                # Fix common JSON formatting issues
                content = content.replace(',}', '}').replace(',]', ']')
                messages = json.loads(content)

        except json.JSONDecodeError:
            # If JSON parsing fails, try line-by-line parsing
            lines = content.split('\n')
            current_obj = ""

            for line in lines:
                line = line.strip()
                if line:
                    current_obj += line
                    if line.endswith('},') or line.endswith('}'):
                        try:
                            # Remove trailing comma and parse
                            obj_str = current_obj.rstrip(',')
                            if not obj_str.startswith('{'):
                                obj_str = '{' + obj_str
                            message = json.loads(obj_str)
                            messages.append(message)
                            current_obj = ""
                        except json.JSONDecodeError:
                            continue

    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    return messages


def parse_timestamp(timestamp_str: str) -> datetime:
    """Convert timestamp string to datetime object for sorting."""
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Try alternative formats if needed
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            print(f"Warning: Could not parse timestamp: {timestamp_str}")
            return datetime.min


def combiner(filepath1: str, filepath2: str, output_filepath: str = None) -> List[Dict[str, Any]]:
    """
    Combine two Discord message files by timestamps to reconstruct conversation.

    Args:
        filepath1: Path to first message file
        filepath2: Path to second message file
        output_filepath: Optional path to save combined messages

    Returns:
        List of combined messages sorted by timestamp
    """
    print(f"Reading messages from {filepath1}...")
    messages1 = parse_message_file(filepath1)
    print(f"Found {len(messages1)} messages in file 1")

    print(f"Reading messages from {filepath2}...")
    messages2 = parse_message_file(filepath2)
    print(f"Found {len(messages2)} messages in file 2")

    # Combine all messages
    all_messages = messages1 + messages2

    # Remove duplicates based on ID
    unique_messages = {}
    for message in all_messages:
        if 'ID' in message:
            unique_messages[message['ID']] = message

    combined_messages = list(unique_messages.values())
    print(f"Combined {len(combined_messages)} unique messages")

    # Sort by timestamp
    def sort_key(message):
        if 'Timestamp' in message:
            return parse_timestamp(message['Timestamp'])
        return datetime.min

    combined_messages.sort(key=sort_key)

    # Save to file if output path provided
    if output_filepath:
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(combined_messages, f, indent=2, ensure_ascii=False)
            print(f"Combined messages saved to {output_filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    return combined_messages


def format_attachments(attachments) -> str:
    """Format attachments for display regardless of their original format."""
    if not attachments:
        return ""

    # Handle different attachment formats
    if isinstance(attachments, list):
        # JSON array format
        formatted = []
        for att in attachments:
            if isinstance(att, dict):
                filename = att.get('filename', att.get('name', 'Unknown file'))
                size = att.get('size', '')
                size_str = f" ({size} bytes)" if size else ""
                formatted.append(f"{filename}{size_str}")
            else:
                formatted.append(str(att))
        return "; ".join(formatted)

    elif isinstance(attachments, str):
        if not attachments.strip():
            return ""

        # Determine separator and split
        separator = None
        items = []

        if ',' in attachments:
            separator = ','
            items = [item.strip() for item in attachments.split(separator) if item.strip()]
        elif ';' in attachments:
            separator = ';'
            items = [item.strip() for item in attachments.split(separator) if item.strip()]
        elif ' ' in attachments.strip():
            # Space-separated (your format)
            separator = ' '
            items = [item.strip() for item in attachments.split() if item.strip()]
        else:
            # Single attachment
            items = [attachments.strip()]

        # Extract filenames from URLs if they're URLs
        formatted_items = []
        for item in items:
            if item.startswith('http'):
                # Extract filename from URL
                filename = item.split('/')[-1].split('?')[0]
                formatted_items.append(filename)
            else:
                formatted_items.append(item)

        return "; ".join(formatted_items)

    return str(attachments)


def print_conversation(messages: List[Dict[str, Any]], limit: int = 20):
    """Print the conversation in a readable format."""
    print(f"\n--- Conversation Timeline (showing first {limit} messages) ---")

    for i, message in enumerate(messages[:limit]):
        timestamp = message.get('Timestamp', 'Unknown time')
        content = message.get('Contents', '')
        msg_id = message.get('ID', 'Unknown ID')
        attachments = message.get('Attachments', '')

        print(f"\n[{timestamp}] ID: {msg_id}")
        if content:
            print(f"  Message: {content}")

        formatted_attachments = format_attachments(attachments)
        if formatted_attachments:
            print(f"  Attachments: {formatted_attachments}")

    if len(messages) > limit:
        print(f"\n... and {len(messages) - limit} more messages")


def get_all_attachments(messages: List[Dict[str, Any]]) -> List[str]:
    """Return a list of all unique attachments in the conversation."""
    all_attachments = []

    for message in messages:
        attachments = message.get('Attachments', '')
        if not attachments:
            continue

        # Parse attachments based on format
        if isinstance(attachments, list):
            # JSON array format
            for att in attachments:
                if isinstance(att, dict):
                    url = att.get('url', att.get('filename', att.get('name', '')))
                    if url:
                        all_attachments.append(url)
                else:
                    all_attachments.append(str(att))

        elif isinstance(attachments, str) and attachments.strip():
            # String format - detect separator
            if ',' in attachments:
                items = [item.strip() for item in attachments.split(',') if item.strip()]
            elif ';' in attachments:
                items = [item.strip() for item in attachments.split(';') if item.strip()]
            elif ' ' in attachments.strip():
                items = [item.strip() for item in attachments.split() if item.strip()]
            else:
                items = [attachments.strip()]

            # Extract filenames from URLs
            all_attachments.extend(items)

    return all_attachments

def get_unique_attachments(messages: List[Dict[str, Any]]) -> List[str]:
    """Return a list of all unique attachments in the conversation."""
    attachments = get_all_attachments(messages)
    unique_attachments = []
    seen = set()
    for att in attachments:
        if att not in seen:
            unique_attachments.append(att)
            seen.add(att)
    return unique_attachments