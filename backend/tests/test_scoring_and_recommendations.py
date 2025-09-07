import pytest
from app.tasks import calculate_accessibility_score, generate_recommendations

class TestAccessibilityScoring:
    """Testy dla funkcji calculate_accessibility_score"""
    
    def test_perfect_score(self):
        """Test dla dokumentu idealnego - wszystkie kryteria spełnione"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 1,
                "has_single_h1": True,
                "has_skipped_levels": False,
                "heading_structure": [1, 2, 2, 3],
                "issues": []
            },
            "image_info": {
                "image_count": 5,
                "images_with_alt": 5,
                "images_without_alt": 0
            }
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=True)
        
        assert result["total_score"] == 100
        assert result["percentage"] == 100
        assert result["level"] == "Wysoki"
        assert len(result["details"]) == 6
        
        # Sprawdź poszczególne kategorie
        details_dict = {d["criterion"]: d for d in result["details"]}
        assert details_dict["Dokument otagowany"]["points"] == 15
        assert details_dict["Metadane dokumentu"]["points"] == 10
        assert details_dict["Struktura nagłówków"]["points"] == 15
    
    def test_worst_case_score(self):
        """Test dla najgorszego możliwego dokumentu"""
        analysis = {
            "is_tagged": False,
            "contains_text": False,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {
                "h1_count": 0,
                "has_single_h1": False,
                "has_skipped_levels": True,
                "issues": ["Brak nagłówków"]
            },
            "image_info": {
                "image_count": 10,
                "images_with_alt": 0,
                "images_without_alt": 10
            }
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        assert result["total_score"] == 0
        assert result["percentage"] == 0
        assert result["level"] == "Bardzo niski"
    
    def test_partial_metadata_score(self):
        """Test dla częściowo wypełnionych metadanych"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,  # Tylko tytuł
            "is_lang_defined": False,  # Brak języka
            "heading_info": {},
            "image_info": {}
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        details_dict = {d["criterion"]: d for d in result["details"]}
        # 5 pkt za tytuł, 0 za język = 5 pkt total
        assert details_dict["Metadane dokumentu"]["points"] == 5
        assert details_dict["Metadane dokumentu"]["max"] == 10
    
    def test_heading_scoring_with_multiple_h1(self):
        """Test punktacji dla wielu nagłówków H1"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {
                "h1_count": 3,  # Za dużo H1
                "has_single_h1": False,
                "has_skipped_levels": False,  # Ale hierarchia OK
                "heading_structure": [1, 1, 1, 2, 3]
            },
            "image_info": {}
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        details_dict = {d["criterion"]: d for d in result["details"]}
        # 3 pkt za H1 (częściowe) + 8 pkt za dobrą hierarchię = 11 pkt
        assert details_dict["Struktura nagłówków"]["points"] == 11
    
    def test_heading_scoring_with_skipped_levels(self):
        """Test punktacji dla pominiętych poziomów nagłówków"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {
                "h1_count": 1,
                "has_single_h1": True,  # Dobry H1
                "has_skipped_levels": True,  # Ale pominięte poziomy
                "heading_structure": [1, 3, 5],  # H1 -> H3 -> H5
                "issues": ["Pominięty poziom: H1 → H3"]
            },
            "image_info": {}
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        details_dict = {d["criterion"]: d for d in result["details"]}
        # 7 pkt za dobry H1 + 4 pkt za częściową strukturę = 11 pkt
        assert details_dict["Struktura nagłówków"]["points"] == 11
    
    def test_image_scoring_partial_alts(self):
        """Test punktacji dla częściowych alt-tekstów"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {},
            "image_info": {
                "image_count": 10,
                "images_with_alt": 7,  # 70% z alt
                "images_without_alt": 3
            }
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        details_dict = {d["criterion"]: d for d in result["details"]}
        # 70% z 20 pkt = 14 pkt
        assert details_dict["Opisy alternatywne obrazów"]["points"] == 14
    
    def test_no_images_gets_full_points(self):
        """Test że brak obrazów daje pełne punkty (nie ma czego sprawdzać)"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {},
            "image_info": {
                "image_count": 0,
                "images_with_alt": 0,
                "images_without_alt": 0
            }
        }
        
        result = calculate_accessibility_score(analysis, is_pdf_ua_compliant=False)
        
        details_dict = {d["criterion"]: d for d in result["details"]}
        assert details_dict["Opisy alternatywne obrazów"]["points"] == 20
        assert details_dict["Opisy alternatywne obrazów"]["max"] == 20
    
    def test_score_levels(self):
        """Test różnych poziomów dostępności"""
    # Bardzo niski (< 40%)
    assert calculate_accessibility_score(
        {"is_tagged": False, "contains_text": False}, False
    )["level"] == "Bardzo niski"
    
    # Niski (40-59%)
    analysis_low = {
        "is_tagged": True,          # 15 pkt
        "contains_text": True,       # 10 pkt
        "is_title_defined": True,    # 5 pkt
        "is_lang_defined": False,    # 0 pkt
        "heading_info": {},          # 0 pkt
        "image_info": {              # 10 pkt (50% z alt)
            "image_count": 10,
            "images_with_alt": 5,
            "images_without_alt": 5
        }
    }
    # Razem: 15+10+5+0+10+0 = 40 pkt = 40%
    result = calculate_accessibility_score(analysis_low, False)
    assert 40 <= result["percentage"] < 60
    assert result["level"] == "Niski"
    
    # Średni (60-84%)
    analysis_medium = {
        "is_tagged": True,           # 15 pkt
        "contains_text": True,        # 10 pkt
        "is_title_defined": True,     # 5 pkt
        "is_lang_defined": True,      # 5 pkt
        "heading_info": {             # 7 pkt (tylko dobry H1)
            "h1_count": 1,
            "has_single_h1": True,
            "has_skipped_levels": True  # Tracę punkty za hierarchię
        },
        "image_info": {               # 10 pkt (50% z alt)
            "image_count": 10,
            "images_with_alt": 5,
            "images_without_alt": 5
        }
    }
    # Razem: 15+10+10+7+10+15 = 67 pkt = 67%
    result = calculate_accessibility_score(analysis_medium, is_pdf_ua_compliant=True)
    assert 60 <= result["percentage"] < 85
    assert result["level"] == "Średni"
    
    # Wysoki (>= 85%)
    analysis_high = {
        "is_tagged": True,            # 15 pkt
        "contains_text": True,         # 10 pkt
        "is_title_defined": True,      # 5 pkt
        "is_lang_defined": True,       # 5 pkt
        "heading_info": {              # 15 pkt (pełne)
            "h1_count": 1,
            "has_single_h1": True,
            "has_skipped_levels": False
        },
        "image_info": {                # 18 pkt (90% z alt)
            "image_count": 10,
            "images_with_alt": 9,
            "images_without_alt": 1
        }
    }
    # Razem: 15+10+10+15+18+30 = 98 pkt = 98%
    result = calculate_accessibility_score(analysis_high, is_pdf_ua_compliant=True)
    assert result["percentage"] >= 85
    assert result["level"] == "Wysoki"


class TestRecommendationsGeneration:
    """Testy dla funkcji generate_recommendations"""
    
    def test_no_recommendations_for_perfect_document(self):
        """Test że idealny dokument dostaje tylko gratulacje"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 1,
                "has_single_h1": True,
                "has_skipped_levels": False
            },
            "image_info": {
                "image_count": 5,
                "images_with_alt": 5,
                "images_without_alt": 0
            }
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        assert len(recommendations) == 1
        assert recommendations[0]["priority"] == "info"
        assert "Gratulacje" in recommendations[0]["issue"]
    
    def test_critical_recommendations_for_untagged(self):
        """Test że brak tagów generuje krytyczną rekomendację"""
        analysis = {
            "is_tagged": False,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {},
            "image_info": {}
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        assert any(r["priority"] == "high" and "tagów struktury" in r["issue"] 
                  for r in recommendations)
        assert any("WCAG 1.3.1" in r.get("wcag_reference", "") 
                  for r in recommendations)
    
    def test_metadata_recommendations(self):
        """Test rekomendacji dla brakujących metadanych"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": False,  # Brak tytułu
            "is_lang_defined": False,   # Brak języka
            "heading_info": {},
            "image_info": {}
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        # Sprawdź rekomendację dla tytułu
        title_rec = next((r for r in recommendations if "tytułu" in r["issue"]), None)
        assert title_rec is not None
        assert title_rec["priority"] == "medium"
        assert "WCAG 2.4.2" in title_rec["wcag_reference"]
        
        # Sprawdź rekomendację dla języka
        lang_rec = next((r for r in recommendations if "język" in r["issue"]), None)
        assert lang_rec is not None
        assert lang_rec["priority"] == "medium"
        assert "WCAG 3.1.1" in lang_rec["wcag_reference"]
    
    def test_heading_recommendations(self):
        """Test rekomendacji dla problemów z nagłówkami"""
        # Test 1: Brak H1
        analysis_no_h1 = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 0,
                "has_single_h1": False,
                "has_skipped_levels": False
            },
            "image_info": {}
        }
        
        recs = generate_recommendations(analysis_no_h1, [])
        h1_rec = next((r for r in recs if "głównego nagłówka H1" in r["issue"]), None)
        assert h1_rec is not None
        assert h1_rec["priority"] == "medium"
        
        # Test 2: Za dużo H1
        analysis_multiple_h1 = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 5,
                "has_single_h1": False,
                "has_skipped_levels": False
            },
            "image_info": {}
        }
        
        recs = generate_recommendations(analysis_multiple_h1, [])
        multi_h1_rec = next((r for r in recs if "Za dużo nagłówków H1" in r["issue"]), None)
        assert multi_h1_rec is not None
        assert multi_h1_rec["priority"] == "low"
        
        # Test 3: Pominięte poziomy
        analysis_skipped = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 1,
                "has_single_h1": True,
                "has_skipped_levels": True,
                "issues": ["Pominięty poziom: H1 → H3"]
            },
            "image_info": {}
        }
        
        recs = generate_recommendations(analysis_skipped, [])
        hierarchy_rec = next((r for r in recs if "hierarchia" in r["issue"]), None)
        assert hierarchy_rec is not None
        assert hierarchy_rec["priority"] == "medium"
    
    def test_image_alt_recommendations(self):
        """Test rekomendacji dla brakujących alt-tekstów"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {},
            "image_info": {
                "image_count": 10,
                "images_with_alt": 3,
                "images_without_alt": 7
            }
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        alt_rec = next((r for r in recommendations if "opisów alternatywnych" in r["issue"]), None)
        assert alt_rec is not None
        assert alt_rec["priority"] == "high"
        assert "7 obrazów" in alt_rec["issue"]
        assert "WCAG 1.1.1" in alt_rec["wcag_reference"]
    
    def test_scanned_pdf_recommendation(self):
        """Test rekomendacji dla zeskanowanego PDF bez tekstu"""
        analysis = {
            "is_tagged": False,
            "contains_text": False,  # Brak tekstu
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {},
            "image_info": {
                "image_count": 10,  # Ale są obrazy
                "images_with_alt": 0,
                "images_without_alt": 10
            }
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        ocr_rec = next((r for r in recommendations if "OCR" in r["recommendation"]), None)
        assert ocr_rec is not None
        assert ocr_rec["priority"] == "high"
        assert "WCAG 1.4.5" in ocr_rec["wcag_reference"]
    
    def test_pdf_ua_recommendations(self):
        """Test rekomendacji dla błędów PDF/UA"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {},
            "image_info": {}
        }
        
        failed_rules = [
            {"description": "Missing Figure tag", "clause": "7.1"},
            {"description": "Invalid table structure", "clause": "7.5"},
            {"description": "Missing TH elements", "clause": "7.5.3"},
            {"description": "Invalid color contrast", "clause": "7.21"},
            {"description": "Missing form labels", "clause": "7.18"}
        ]
        
        recommendations = generate_recommendations(analysis, failed_rules)
        
        # Sprawdź że pokazuje max 3 szczegółowe błędy
        pdf_ua_recs = [r for r in recommendations if "Naruszenie PDF/UA" in r["issue"]]
        assert len(pdf_ua_recs) == 3
        
        # Sprawdź że jest zbiorcza rekomendacja dla pozostałych
        summary_rec = next((r for r in recommendations if "Pozostałe" in r["issue"]), None)
        assert summary_rec is not None
        assert "2 błędy" in summary_rec["issue"]
        assert summary_rec["priority"] == "low"
    
    def test_recommendations_are_sorted_by_priority(self):
        """Test że rekomendacje są posortowane według priorytetu"""
        analysis = {
            "is_tagged": False,  # high priority
            "contains_text": True,
            "is_title_defined": False,  # medium priority
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 3,  # low priority
                "has_single_h1": False
            },
            "image_info": {}
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        # Sprawdź kolejność priorytetów
        priorities = [r["priority"] for r in recommendations]
        
        # high powinno być przed medium
        high_index = priorities.index("high") if "high" in priorities else float('inf')
        medium_index = priorities.index("medium") if "medium" in priorities else float('inf')
        low_index = priorities.index("low") if "low" in priorities else float('inf')
        
        assert high_index < medium_index
        assert medium_index < low_index
    
    def test_single_image_grammar(self):
        """Test że używa poprawnej gramatyki dla pojedynczego obrazu"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {},
            "image_info": {
                "image_count": 1,
                "images_with_alt": 0,
                "images_without_alt": 1
            }
        }
        
        recommendations = generate_recommendations(analysis, [])
        
        alt_rec = next((r for r in recommendations if "opisów alternatywnych" in r["issue"]), None)
        assert "1 obrazu" in alt_rec["issue"]  # "obrazu" nie "obrazów"


class TestIntegration:
    """Testy integracyjne sprawdzające współdziałanie obu funkcji"""
    
    def test_low_score_generates_multiple_recommendations(self):
        """Test że niski wynik generuje wiele rekomendacji"""
        analysis = {
            "is_tagged": False,
            "contains_text": False,
            "is_title_defined": False,
            "is_lang_defined": False,
            "heading_info": {"h1_count": 0},
            "image_info": {"image_count": 5, "images_with_alt": 0, "images_without_alt": 5}
        }
        
        score_result = calculate_accessibility_score(analysis, False)
        recommendations = generate_recommendations(analysis, [])
        
        assert score_result["percentage"] < 20
        assert score_result["level"] == "Bardzo niski"
        assert len(recommendations) >= 5  # Powinno być dużo rekomendacji
        
        # Sprawdź że są krytyczne rekomendacje
        high_priority_count = sum(1 for r in recommendations if r["priority"] == "high")
        assert high_priority_count >= 2
    
    def test_high_score_generates_few_recommendations(self):
        """Test że wysoki wynik generuje mało rekomendacji"""
        analysis = {
            "is_tagged": True,
            "contains_text": True,
            "is_title_defined": True,
            "is_lang_defined": True,
            "heading_info": {
                "h1_count": 1,
                "has_single_h1": True,
                "has_skipped_levels": False
            },
            "image_info": {
                "image_count": 5,
                "images_with_alt": 4,  # Prawie idealne
                "images_without_alt": 1
            }
        }
        
        score_result = calculate_accessibility_score(analysis, True)
        recommendations = generate_recommendations(analysis, [])
        
        assert score_result["percentage"] >= 85
        assert score_result["level"] == "Wysoki"
        assert len(recommendations) <= 2  # Maksymalnie drobne uwagi


if __name__ == "__main__":
    pytest.main([__file__, "-v"])