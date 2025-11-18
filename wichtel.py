#!/usr/bin/env python3
"""
Secret Santa (Wichtel) Matching Script
Generates Secret Santa assignments with couple constraints and sends secret notifications.
"""

import json
import random
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Tuple, Optional


class SecretSanta:
    def __init__(self, config_file: str):
        """Initialize Secret Santa with configuration file."""
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.participants = self.config['participants']
        self.couples = self.config.get('couples', [])
        self.email_config = self.config.get('email_config', {})
        self.validate_config()

    def validate_config(self):
        """Validate the configuration."""
        if len(self.participants) < 3:
            raise ValueError("Need at least 3 participants for Secret Santa")

        # Check all participants have required fields
        for p in self.participants:
            if 'name' not in p or 'email' not in p:
                raise ValueError(f"Participant missing name or email: {p}")

        # Validate couples exist in participants
        names = {p['name'] for p in self.participants}
        for couple in self.couples:
            if len(couple) != 2:
                raise ValueError(f"Couple must have exactly 2 people: {couple}")
            for person in couple:
                if person not in names:
                    raise ValueError(f"Person in couple not found in participants: {person}")

    def create_matching(self, max_attempts: int = 1000) -> Dict[str, str]:
        """
        Create a valid Secret Santa matching.
        Returns a dictionary mapping giver name to receiver name.
        """
        for attempt in range(max_attempts):
            matching = self._attempt_matching()
            if matching:
                return matching

        raise RuntimeError("Could not find valid matching after maximum attempts. "
                         "This might happen if constraints are too restrictive.")

    def _attempt_matching(self) -> Optional[Dict[str, str]]:
        """Attempt to create a valid matching."""
        names = [p['name'] for p in self.participants]
        receivers = names.copy()
        random.shuffle(receivers)

        matching = {}

        for giver in names:
            # Find valid receiver
            valid_receivers = [
                r for r in receivers
                if r != giver and not self._is_couple(giver, r)
            ]

            if not valid_receivers:
                return None  # Invalid matching, try again

            receiver = valid_receivers[0]
            matching[giver] = receiver
            receivers.remove(receiver)

        # Verify it forms a valid cycle (no short loops)
        if not self._is_valid_cycle(matching):
            return None

        return matching

    def _is_couple(self, person1: str, person2: str) -> bool:
        """Check if two people are a couple."""
        for couple in self.couples:
            if set([person1, person2]) == set(couple):
                return True
        return False

    def _is_valid_cycle(self, matching: Dict[str, str]) -> bool:
        """
        Verify that the matching forms one complete cycle.
        This prevents short loops like A->B->A while C->D->C.
        """
        if not matching:
            return False

        start = next(iter(matching.keys()))
        current = start
        visited = set()

        while current not in visited:
            visited.add(current)
            current = matching[current]

            if current == start:
                # Check if we visited everyone
                return len(visited) == len(matching)

        return False

    def send_notifications(self, matching: Dict[str, str], dry_run: bool = False):
        """
        Send email notifications to all participants.
        If dry_run is True, just print what would be sent.
        """
        if dry_run:
            print("\n=== DRY RUN MODE - No emails will be sent ===\n")

        email_map = {p['name']: p['email'] for p in self.participants}

        success_count = 0
        for giver, receiver in matching.items():
            giver_email = email_map[giver]

            if dry_run:
                print(f"Would send email to: {giver} ({giver_email})")
                print(f"  Message: You are Secret Santa for {receiver}")
                print()
            else:
                try:
                    self._send_email(giver, giver_email, receiver)
                    success_count += 1
                    # Don't print the matching to keep it secret!
                    print(f"✓ Notification sent to {giver}")
                except Exception as e:
                    print(f"✗ Failed to send to {giver}: {str(e)}")

        if not dry_run:
            print(f"\n{success_count}/{len(matching)} notifications sent successfully!")
            print("\n⚠️  The matching is now secret - even you don't know who has whom!")

    def _send_email(self, giver_name: str, giver_email: str, receiver_name: str):
        """Send email notification to a participant."""
        subject = self.email_config.get('subject', '🎄 Your Secret Santa Assignment')

        # Create message body
        body = self.email_config.get('message_template',
            "Hello {giver},\n\n"
            "You are the Secret Santa for: {receiver}\n\n"
            "Happy gifting! 🎁\n"
        ).format(giver=giver_name, receiver=receiver_name)

        # Create email
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from_email']
        msg['To'] = giver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(self.email_config['smtp_server'],
                         self.email_config.get('smtp_port', 587)) as server:
            server.starttls()
            server.login(self.email_config['from_email'],
                        self.email_config['password'])
            server.send_message(msg)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Secret Santa (Wichtel) matching with couple constraints'
    )
    parser.add_argument(
        'config',
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be sent without actually sending emails'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducible matching (useful for testing)'
    )

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    try:
        # Initialize Secret Santa
        santa = SecretSanta(args.config)

        print("🎄 Secret Santa Matching System 🎁")
        print(f"\nParticipants: {len(santa.participants)}")
        print(f"Couples: {len(santa.couples)}")

        # Create matching
        print("\nGenerating matching...")
        matching = santa.create_matching()
        print("✓ Valid matching created!")

        # Send notifications
        print("\nSending notifications...")
        santa.send_notifications(matching, dry_run=args.dry_run)

    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
