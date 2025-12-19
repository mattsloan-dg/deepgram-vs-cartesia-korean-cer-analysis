def levenshtein_with_operations(source, target):
    """
    Calculate Levenshtein distance and count operations.
    
    This function measures how many single-character edits (insertions, deletions, 
    or substitutions) are needed to transform the source string into the target string.
    
    For Korean speech-to-text: 
    - source = ground truth transcript
    - target = model's predicted transcript
    - The distance tells you how many character errors the model made
    
    Returns:
        (distance, insertions, deletions, substitutions)
        - distance: total number of edits needed (this is your CER numerator)
        - insertions: how many characters the model added that shouldn't be there
        - deletions: how many characters the model missed
        - substitutions: how many characters the model got wrong
    """
    m, n = len(source), len(target)
    
    # Create DP table
    # This is a 2D grid where each cell [i,j] will store the minimum number of 
    # edits needed to transform the first i characters of source into the 
    # first j characters of target
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    # First column: to transform i characters into an empty string, delete all i
    for i in range(m + 1):
        dp[i][0] = i  # Cost of i deletions
    
    # First row: to transform empty string into j characters, insert all j
    for j in range(n + 1):
        dp[0][j] = j  # Cost of j insertions
    
    # Fill DP table
    # Work through each position, building up from smaller subproblems
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if source[i-1] == target[j-1]:
                # Characters match! No operation needed.
                # Just copy the cost from the diagonal (previous characters)
                dp[i][j] = dp[i-1][j-1]
            else:
                # Characters don't match. We need to do one operation.
                # Pick whichever operation gives us the minimum total cost:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # Deletion: remove char from source
                    dp[i][j-1],      # Insertion: add char to source
                    dp[i-1][j-1]     # Substitution: replace char in source
                )
    
    # Now we have the minimum distance in dp[m][n], but we also want to know
    # HOW MANY of each operation type were used. Time to backtrack!
    
    insertions = 0
    deletions = 0
    substitutions = 0
    
    # Start at bottom-right corner (full strings) and work backwards to top-left (empty strings)
    i, j = m, n
    while i > 0 or j > 0:
        # Edge case: we've exhausted the source string
        if i == 0:
            # Only way to continue is inserting remaining target characters
            insertions += j
            break
        # Edge case: we've exhausted the target string
        elif j == 0:
            # Only way to continue is deleting remaining source characters
            deletions += i
            break
        # Normal case: check if current characters match
        elif source[i-1] == target[j-1]:
            # Characters match, so we move diagonally back with no operation
            i -= 1
            j -= 1
        else:
            # Characters don't match. Figure out which operation got us here
            # by checking which adjacent cell has the minimum value
            
            # Calculate the cost if we came from each direction
            deletion_cost = dp[i-1][j] if i > 0 else float('inf')
            insertion_cost = dp[i][j-1] if j > 0 else float('inf')
            substitution_cost = dp[i-1][j-1] if i > 0 and j > 0 else float('inf')
            
            # Find which operation was actually used (the one with minimum cost)
            min_cost = min(deletion_cost, insertion_cost, substitution_cost)
            
            # Move in the direction of the minimum cost and count that operation
            if min_cost == substitution_cost:
                # We substituted: moved diagonally
                substitutions += 1
                i -= 1
                j -= 1
            elif min_cost == deletion_cost:
                # We deleted from source: moved up
                deletions += 1
                i -= 1
            else:  # insertion_cost
                # We inserted into source: moved left
                insertions += 1
                j -= 1
    
    # Return the total distance and breakdown of each operation type
    # For CER calculation: CER = distance / len(source) * 100
    return dp[m][n], insertions, deletions, substitutions