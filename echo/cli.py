"""
Command-line interface for Echo Memory System
"""

import argparse
import json
from .core import MemorySystem


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Echo - Brain-Like Memory System")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new memory")
    create_parser.add_argument("--title", required=True, help="Memory title")
    create_parser.add_argument("--content", required=True, help="Memory content")
    create_parser.add_argument("--category", default="learning", help="Memory category")
    create_parser.add_argument("--priority", default="P1", help="Priority (P0/P1/P2)")
    create_parser.add_argument("--permanent", action="store_true", help="Never decay")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    
    # Access command
    access_parser = subparsers.add_parser("access", help="Access a memory")
    access_parser.add_argument("memory_id", help="Memory ID")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Decay command
    subparsers.add_parser("decay", help="Apply temperature decay")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export memories")
    export_parser.add_argument("--output", default="memories_export.json", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize memory system
    memory = MemorySystem()
    
    if args.command == "create":
        mem_id = memory.create(
            title=args.title,
            content=args.content,
            category=args.category,
            priority=args.priority,
            permanent=args.permanent
        )
        print(f"Created memory: {mem_id}")
    
    elif args.command == "search":
        results = memory.search(args.query, limit=args.limit)
        print(f"\nFound {len(results)} results:\n")
        for mem, score in results:
            print(f"[{mem['id']}] {mem['title']}")
            print(f"  Score: {score:.2f} | Temp: {mem['temperature']:.2f}")
            print()
    
    elif args.command == "access":
        mem = memory.access(args.memory_id)
        if mem:
            print(f"Accessed: {mem['title']}")
            print(f"Temperature: {mem['temperature']:.2f}")
        else:
            print(f"Memory not found: {args.memory_id}")
    
    elif args.command == "stats":
        stats = memory.get_stats()
        print("\n=== Echo Memory Statistics ===\n")
        print(f"Total memories: {stats['total_memories']}")
        print(f"\nBy state:")
        for state, count in stats['by_state'].items():
            print(f"  {state}: {count}")
        print(f"\nBy category:")
        for cat, count in stats['by_category'].items():
            print(f"  {cat}: {count}")
        print(f"\nAverage temperature: {stats['avg_temperature']:.2f}")
    
    elif args.command == "decay":
        stats = memory.decay_temperatures()
        print(f"Decay applied to {stats['processed']} memories")
        print(f"State changes: {stats['state_changes']}")
    
    elif args.command == "export":
        memory.export(args.output)
        print(f"Exported to: {args.output}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
