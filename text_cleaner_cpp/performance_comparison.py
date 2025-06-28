#!/usr/bin/env python3
"""
Performance comparison: C++ Cython vs Pure Python text processing
"""

import time
import random
import string
from typing import List, Dict
import statistics

# Import your Cython wrapper
try:
    from speech_clean_wrapper import PyCleanText
    CYTHON_AVAILABLE = True
except ImportError:
    print("Warning: Cython wrapper not available. Install with: python3 setup_cython.py build_ext --inplace")
    CYTHON_AVAILABLE = False

class PythonTextCleaner:
    """Pure Python implementation for comparison"""
    
    def __init__(self, raw_text: str, file_name: str, min_chars: int):
        self.raw_text = raw_text
        self.file_name = file_name
        self.min_chars = min_chars
        self.sentences = []
        self.cleaned_text = ""
        self.num_sentences = 0
    
    def is_ascii_only(self, sentence: str) -> bool:
        """Check if sentence contains only ASCII characters"""
        return all(ord(c) < 128 for c in sentence)
    
    def split_punctuation(self, text: str) -> List[str]:
        """Split text on sentence-ending punctuation"""
        results = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                if current_sentence.strip():
                    results.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            results.append(current_sentence.strip())
        
        return results
    
    def process_text(self):
        """Process and clean the text"""
        raw_sentences = self.split_punctuation(self.raw_text)
        
        for sentence in raw_sentences:
            # Clean whitespace
            sentence = sentence.strip()
            
            if self.is_ascii_only(sentence) and len(sentence) >= self.min_chars:
                self.sentences.append(sentence)
                self.cleaned_text += sentence
                self.num_sentences += 1
        
        print(f"Number of lines processed: {self.num_sentences}")
    
    def write_to_file(self) -> int:
        """Write cleaned sentences to file"""
        try:
            with open(self.file_name, 'w') as file:
                for sentence in self.sentences:
                    file.write(sentence + '\n')
            return 1
        except Exception as e:
            print(f"Error writing to file: {e}")
            return 0
    
    def get_sentences(self) -> List[str]:
        """Get cleaned sentences"""
        return self.sentences
    
    def get_sentence_count(self) -> int:
        """Get number of sentences"""
        return self.num_sentences

def generate_test_text(num_sentences: int = 1000, avg_sentence_length: int = 50) -> str:
    """Generate random test text"""
    sentences = []
    
    for _ in range(num_sentences):
        # Generate random sentence length
        length = random.randint(avg_sentence_length // 2, avg_sentence_length * 2)
        
        # Generate random words
        words = []
        for _ in range(length // 5):  # Assume average word length of 5
            word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            words.append(word)
        
        # Create sentence
        sentence = ' '.join(words).capitalize()
        
        # Add random punctuation
        if random.random() < 0.7:  # 70% chance of period
            sentence += '.'
        elif random.random() < 0.5:  # 15% chance of exclamation
            sentence += '!'
        else:  # 15% chance of question
            sentence += '?'
        
        sentences.append(sentence)
    
    return ' '.join(sentences)

def benchmark_implementation(cleaner_class, test_text: str, num_runs: int = 10) -> Dict:
    """Benchmark a text cleaning implementation"""
    times = []
    sentence_counts = []
    
    for i in range(num_runs):
        # Create fresh instance
        cleaner = cleaner_class(
            raw_text=test_text,
            file_name=f"temp_output_{i}.txt",
            min_chars=10
        )
        
        # Time the processing
        start_time = time.perf_counter()
        cleaner.process_text()
        end_time = time.perf_counter()
        
        times.append(end_time - start_time)
        sentence_counts.append(cleaner.get_sentence_count())
    
    return {
        'times': times,
        'sentence_counts': sentence_counts,
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'avg_sentences': statistics.mean(sentence_counts)
    }

def run_performance_test():
    """Run comprehensive performance comparison"""
    print("=" * 60)
    print("PERFORMANCE COMPARISON: C++ Cython vs Pure Python")
    print("=" * 60)
    
    # Test different text sizes
    test_sizes = [
        (100, "Small text (100 sentences)"),
        (500, "Medium text (500 sentences)"),
        (1000, "Large text (1000 sentences)"),
        (2000, "Very large text (2000 sentences)")
    ]
    
    results = {}
    
    for num_sentences, description in test_sizes:
        print(f"\n{description}")
        print("-" * 40)
        
        # Generate test text
        test_text = generate_test_text(num_sentences, avg_sentence_length=60)
        print(f"Generated text: {len(test_text)} characters, ~{num_sentences} sentences")
        
        # Test Python implementation
        print("\nTesting Pure Python implementation...")
        python_results = benchmark_implementation(PythonTextCleaner, test_text, num_runs=5)
        
        print(f"  Average time: {python_results['avg_time']:.4f}s")
        print(f"  Min time: {python_results['min_time']:.4f}s")
        print(f"  Max time: {python_results['max_time']:.4f}s")
        print(f"  Sentences processed: {python_results['avg_sentences']:.1f}")
        
        # Test Cython implementation if available
        if CYTHON_AVAILABLE:
            print("\nTesting C++ Cython implementation...")
            cython_results = benchmark_implementation(PyCleanText, test_text, num_runs=5)
            
            print(f"  Average time: {cython_results['avg_time']:.4f}s")
            print(f"  Min time: {cython_results['min_time']:.4f}s")
            print(f"  Max time: {cython_results['max_time']:.4f}s")
            print(f"  Sentences processed: {cython_results['avg_sentences']:.1f}")
            
            # Calculate speedup
            speedup = python_results['avg_time'] / cython_results['avg_time']
            print(f"\n  🚀 SPEEDUP: {speedup:.2f}x faster")
            
            # Store results
            results[description] = {
                'python': python_results,
                'cython': cython_results,
                'speedup': speedup
            }
        else:
            results[description] = {
                'python': python_results,
                'cython': None,
                'speedup': None
            }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if CYTHON_AVAILABLE:
        print(f"{'Text Size':<25} {'Python (s)':<12} {'Cython (s)':<12} {'Speedup':<10}")
        print("-" * 60)
        
        for description, result in results.items():
            python_time = result['python']['avg_time']
            cython_time = result['cython']['avg_time']
            speedup = result['speedup']
            
            print(f"{description:<25} {python_time:<12.4f} {cython_time:<12.4f} {speedup:<10.2f}x")
        
        # Overall average speedup
        avg_speedup = statistics.mean([r['speedup'] for r in results.values() if r['speedup']])
        print(f"\n Average speedup: {avg_speedup:.2f}x")
        
        if avg_speedup > 5:
            print("🔥 Excellent performance improvement!")
        elif avg_speedup > 2:
            print("⚡ Good performance improvement!")
        else:
            print(" Modest performance improvement")
    else:
        print("Cython implementation not available for comparison")

def test_correctness():
    """Test that both implementations produce the same results"""
    print("\n" + "=" * 60)
    print("CORRECTNESS TEST")
    print("=" * 60)
    
    # Simple test text
    test_text = "This is the first sentence. This is the second sentence! And this is the third sentence?"
    
    # Python implementation
    python_cleaner = PythonTextCleaner(test_text, "python_test.txt", min_chars=10)
    python_cleaner.process_text()
    python_sentences = python_cleaner.get_sentences()
    
    print(f"Python processed {len(python_sentences)} sentences:")
    for i, sentence in enumerate(python_sentences, 1):
        print(f"  {i}. {sentence}")
    
    if CYTHON_AVAILABLE:
        # Cython implementation
        cython_cleaner = PyCleanText(test_text, "cython_test.txt", min_chars=10)
        cython_cleaner.process_text()
        cython_sentences = cython_cleaner.get_sentences()
        
        print(f"\nCython processed {len(cython_sentences)} sentences:")
        for i, sentence in enumerate(cython_sentences, 1):
            print(f"  {i}. {sentence}")
        
        # Compare results
        if python_sentences == cython_sentences:
            print("\n✅ CORRECTNESS TEST PASSED: Both implementations produce identical results!")
        else:
            print("\n❌ CORRECTNESS TEST FAILED: Implementations produce different results!")
            print("Python sentences:", python_sentences)
            print("Cython sentences:", cython_sentences)

if __name__ == "__main__":
    # Run correctness test first
    test_correctness()
    
    # Run performance comparison
    run_performance_test()
    
    print("\n" + "=" * 60)
    print("Performance test completed!")
    print("=" * 60) 