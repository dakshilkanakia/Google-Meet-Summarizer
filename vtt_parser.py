import re
from datetime import datetime
from typing import List, Dict, Tuple

class VTTParser:
    def __init__(self):
        self.speakers = set()
        self.conversations = []
    
    def parse_vtt_file(self, file_path: str) -> Dict:
        """
        Parse a VTT file and extract structured conversation data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Split into blocks (each subtitle block)
            blocks = content.split('\n\n')
            
            conversations = []
            speakers = set()
            
            for block in blocks:
                if not block.strip() or block.strip() == 'WEBVTT':
                    continue
                
                lines = block.strip().split('\n')
                if len(lines) < 3:
                    continue
                
                # Parse timestamp line (line 1)
                timestamp_line = lines[1]
                if '-->' not in timestamp_line:
                    continue
                
                start_time, end_time = self._parse_timestamp(timestamp_line)
                
                # Parse speaker and text (line 2+)
                speaker_text = ' '.join(lines[2:])
                speaker, text = self._extract_speaker_and_text(speaker_text)
                
                if speaker and text:
                    speakers.add(speaker)
                    conversations.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'speaker': speaker,
                        'text': text.strip()
                    })
            
            return {
                'conversations': conversations,
                'speakers': list(speakers),
                'total_entries': len(conversations),
                'file_path': file_path
            }
            
        except Exception as e:
            print(f"Error parsing VTT file: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_line: str) -> Tuple[str, str]:
        """
        Parse timestamp line: '00:00:05.640 --> 00:00:17.960'
        """
        try:
            times = timestamp_line.split(' --> ')
            start_time = times[0].strip()
            end_time = times[1].strip()
            return start_time, end_time
        except:
            return "", ""
    
    def _extract_speaker_and_text(self, speaker_text: str) -> Tuple[str, str]:
        """
        Extract speaker name and text from lines like:
        'adamnoel: Drive in teams. I think that's what they want.'
        """
        # Look for pattern: speaker_name: text
        match = re.match(r'^([^:]+):\s*(.+)$', speaker_text)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            return speaker, text
        
        # If no speaker pattern found, treat as continuation
        return "", speaker_text
    
    def get_conversation_text(self, parsed_data: Dict) -> str:
        """
        Convert parsed conversations back to readable text format
        """
        if not parsed_data or 'conversations' not in parsed_data:
            return ""
        
        text_blocks = []
        current_speaker = ""
        current_text = ""
        
        for conv in parsed_data['conversations']:
            speaker = conv['speaker']
            text = conv['text']
            
            if speaker == current_speaker:
                # Same speaker continuing
                current_text += " " + text
            else:
                # New speaker or first entry
                if current_speaker and current_text:
                    text_blocks.append(f"{current_speaker}: {current_text}")
                
                current_speaker = speaker
                current_text = text
        
        # Add the last block
        if current_speaker and current_text:
            text_blocks.append(f"{current_speaker}: {current_text}")
        
        return "\n\n".join(text_blocks)
    
    def get_meeting_stats(self, parsed_data: Dict) -> Dict:
        """
        Get basic statistics about the meeting
        """
        if not parsed_data:
            return {}
        
        conversations = parsed_data.get('conversations', [])
        if not conversations:
            return {}
        
        # Calculate duration
        start_time = conversations[0]['start_time']
        end_time = conversations[-1]['end_time']
        
        # Count words per speaker
        speaker_stats = {}
        for conv in conversations:
            speaker = conv['speaker']
            if speaker:
                word_count = len(conv['text'].split())
                if speaker in speaker_stats:
                    speaker_stats[speaker] += word_count
                else:
                    speaker_stats[speaker] = word_count
        
        return {
            'duration': f"{start_time} to {end_time}",
            'total_speakers': len(parsed_data.get('speakers', [])),
            'total_entries': len(conversations),
            'speaker_word_counts': speaker_stats
        }


# Test the parser
if __name__ == "__main__":
    parser = VTTParser()
    
    # Test with a sample file (you'll need to provide the path)
    # parsed_data = parser.parse_vtt_file("path_to_your_vtt_file.vtt")
    # 
    # if parsed_data:
    #     print("Speakers:", parsed_data['speakers'])
    #     print("\nStats:", parser.get_meeting_stats(parsed_data))
    #     print("\nConversation text:")
    #     print(parser.get_conversation_text(parsed_data))
    
    print("VTT Parser ready!")