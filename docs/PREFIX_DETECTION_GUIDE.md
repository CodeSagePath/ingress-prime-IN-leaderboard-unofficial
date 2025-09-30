# "Time Span Agent Name" Prefix Detection Guide

## Overview

The Ingress Leaderboard Bot now supports configurable prefix detection for the "Time Span Agent Name" pattern. This feature allows you to control how the bot recognizes and processes Ingress statistics data.

## How It Works

The bot looks for the exact pattern `Time Span Agent Name` anywhere in your message. When found, it:

1. **Recognizes** the message as containing Ingress statistics data
2. **Removes** the prefix pattern from the data before processing
3. **Provides enhanced feedback** about the detection

## Configuration Modes

### Flexible Mode (Default)
- **Behavior**: Processes ALL messages, but gives priority to those with the prefix
- **Use case**: General use where you want the bot to be helpful and responsive
- **Setting**: `PREFIX_DETECTION_MODE=flexible`

### Strict Mode
- **Behavior**: ONLY processes messages containing "Time Span Agent Name"
- **Use case**: When you want the bot to ignore all messages except those with proper Ingress data
- **Setting**: `PREFIX_DETECTION_MODE=strict`

## Configuration

### Method 1: Environment Variable
```bash
# Set to strict mode
export PREFIX_DETECTION_MODE=strict

# Set to flexible mode (default)
export PREFIX_DETECTION_MODE=flexible
```

### Method 2: .env File
Edit the `.env` file in your project root:
```
PREFIX_DETECTION_MODE=strict
```

## Usage Examples

### ✅ Valid Messages (Processed in Both Modes)

1. **Complete Ingress Header**:
```
Time Span Agent Name Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level Lifetime AP Current AP ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000 1500...
```

2. **Prefix at Start**:
```
Time Span Agent Name here is my data: ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000...
```

3. **Prefix in Middle**:
```
Here are my stats: Time Span Agent Name Agent Faction Date ALL TIME TestAgent Enlightened 2025-01-15...
```

4. **Case Insensitive**:
```
time span agent name ALL TIME TestAgent Enlightened 2025-01-15 12:30:45...
```

### ❌ Messages Without Prefix

**Flexible Mode**: Still processed, but with lower priority
```
ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000...
```

**Strict Mode**: Ignored completely (bot provides guidance message)
```
ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000...
```

## Bot Responses

### When Prefix is Found
```
✅ Perfect! I found the required prefix: `Time Span Agent Name`

🎯 Processing your Ingress statistics...
```

### When Prefix is Missing (Strict Mode)
```
🚫 Prefix Required

To submit Ingress statistics, your message must contain:
`Time Span Agent Name`

💡 How to fix:
1. Copy your complete Ingress statistics
2. Make sure it includes the header with `Time Span Agent Name`
3. Paste the complete data including the header
```

### When Prefix is Missing (Flexible Mode)
```
📊 Processing your data...

💡 Pro tip: Including the header `Time Span Agent Name` helps me identify Ingress data faster!
```

## Technical Details

### Pattern Detection
- **Pattern**: `Time Span Agent Name` (exact match)
- **Case Sensitive**: No (matches `time span agent name`, `TIME SPAN AGENT NAME`, etc.)
- **Location**: Can be anywhere in the message (start, middle, end)
- **Cleaning**: Pattern is removed from the data before processing

### Processing Flow
1. Check if message contains "Time Span Agent Name"
2. If strict mode and no prefix → ignore message
3. If prefix found → remove it and process clean data
4. Parse the cleaned data using existing Ingress data parser
5. Provide appropriate feedback to user

## Testing

Run the test script to verify the implementation:
```bash
# Test with current settings
python test_prefix_detection.py

# Test in strict mode
PREFIX_DETECTION_MODE=strict python test_prefix_detection.py

# Test in flexible mode
PREFIX_DETECTION_MODE=flexible python test_prefix_detection.py
```

## Migration Guide

### From Existing Setup
1. **No changes needed** - flexible mode is default and maintains existing behavior
2. **To enable strict mode** - set `PREFIX_DETECTION_MODE=strict` in your `.env` file
3. **Existing data** - all existing functionality remains unchanged

### For New Deployments
1. Choose your preferred mode based on use case
2. Set the environment variable accordingly
3. Test with sample data to ensure expected behavior

## Troubleshooting

### Bot Not Responding (Strict Mode)
- **Cause**: Message doesn't contain "Time Span Agent Name"
- **Solution**: Include the prefix in your message

### Bot Still Processing Everything (Expected in Flexible Mode)
- **Cause**: Flexible mode processes all messages
- **Solution**: Switch to strict mode if you want prefix-only processing

### Case Sensitivity Issues
- **Note**: Pattern matching is case-insensitive by default
- **Verification**: Test with different cases to confirm

## Advanced Configuration

The system supports additional configuration options in `config/settings.py`:

```python
PREFIX_SETTINGS = {
    "strict_mode": PREFIX_DETECTION_MODE == "strict",
    "required_pattern": "Time Span Agent Name",
    "case_sensitive": False,
    "pattern_anywhere": True,
    "ignore_without_prefix": PREFIX_DETECTION_MODE == "strict",
}
```

## Support

If you encounter issues:
1. Check your `PREFIX_DETECTION_MODE` setting
2. Run the test script to verify functionality
3. Check bot logs for prefix detection messages
4. Ensure your Ingress data includes the complete header